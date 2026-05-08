export type Version = number[];

export type Capability = {
  name: string;
  version: Version;
  traits?: string[];
};

export type Context = {
  config: Record<string, unknown>;
  bind(capability: Capability, value: unknown): void;
  resolve<T = unknown>(name: string, minVersion?: Version, traits?: string[]): T;
  listBindings(): Capability[];
};

export type ModuleSpec = {
  name: string;
  provides: Capability[];
  requires: Capability[];
  start(ctx: Context): void | Promise<void>;
  stop?(ctx: Context): void | Promise<void>;
};

export type AdapterSpec = {
  src: Capability;
  dst: Capability;
  build(ctx: Context): unknown;
};

function compareVersion(a: Version, b: Version): number {
  const n = Math.max(a.length, b.length);
  for (let i = 0; i < n; i += 1) {
    const ai = a[i] ?? 0;
    const bi = b[i] ?? 0;
    if (ai !== bi) return ai - bi;
  }
  return 0;
}

export function compatible(need: Capability, provider: Capability): boolean {
  const requiredTraits = new Set(need.traits ?? []);
  const providerTraits = new Set(provider.traits ?? []);
  for (const trait of requiredTraits) {
    if (!providerTraits.has(trait)) return false;
  }
  return need.name === provider.name && compareVersion(provider.version, need.version) >= 0;
}

function capKey(capability: Capability): string {
  return `${capability.name}@${capability.version.join(".")}|${(capability.traits ?? []).sort().join(",")}`;
}

export class LatticeContext implements Context {
  public config: Record<string, unknown>;
  private bindings = new Map<string, { capability: Capability; value: unknown }>();

  constructor(config: Record<string, unknown> = {}) {
    this.config = config;
  }

  bind(capability: Capability, value: unknown): void {
    this.bindings.set(capKey(capability), { capability, value });
  }

  resolve<T = unknown>(name: string, minVersion: Version = [0], traits: string[] = []): T {
    const need: Capability = { name, version: minVersion, traits };
    const matches = [...this.bindings.values()].filter(({ capability }) => compatible(need, capability));
    if (matches.length === 0) throw new Error(`No binding for ${name} >= ${minVersion.join(".")}`);
    matches.sort((a, b) => compareVersion(b.capability.version, a.capability.version));
    return matches[0].value as T;
  }

  listBindings(): Capability[] {
    return [...this.bindings.values()].map((x) => x.capability);
  }

  clear(): void {
    this.bindings.clear();
  }
}

export class Kernel {
  public ctx = new LatticeContext();
  private started: ModuleSpec[] = [];

  constructor(public modules: ModuleSpec[], public adapters: AdapterSpec[] = []) {}

  private findProvider(need: Capability): Capability | undefined {
    return this.ctx.listBindings().find((have) => compatible(need, have));
  }

  private tryAdapt(need: Capability): Capability | undefined {
    for (const adapter of this.adapters) {
      if (!compatible(need, adapter.dst)) continue;
      const src = this.ctx.listBindings().find((bound) => compatible(adapter.src, bound));
      if (!src) continue;
      this.ctx.bind(adapter.dst, adapter.build(this.ctx));
      return adapter.dst;
    }
    return undefined;
  }

  private requirementsSatisfied(module: ModuleSpec): boolean {
    for (const requirement of module.requires) {
      if (!this.findProvider(requirement) && !this.tryAdapt(requirement)) return false;
    }
    return true;
  }

  private requirementSatisfiedByVirtual(need: Capability, available: Capability[]): boolean {
    if (available.some((have) => compatible(need, have))) return true;
    return this.adapters.some(
      (adapter) =>
        compatible(need, adapter.dst) && available.some((have) => compatible(adapter.src, have)),
    );
  }

  private startOrder(): ModuleSpec[] {
    const pending = [...this.modules];
    const order: ModuleSpec[] = [];
    const available: Capability[] = [];
    let changed = true;

    while (pending.length > 0 && changed) {
      changed = false;
      for (const module of [...pending]) {
        if (module.requires.every((req) => this.requirementSatisfiedByVirtual(req, available))) {
          order.push(module);
          pending.splice(pending.indexOf(module), 1);
          available.push(...module.provides);
          changed = true;
        }
      }
    }

    if (pending.length > 0) {
      throw new Error(`Unresolvable modules: ${pending.map((m) => m.name).join(", ")}`);
    }

    return order;
  }

  private ensureRuntimeRequirements(module: ModuleSpec): void {
    for (const requirement of module.requires) {
      if (!this.findProvider(requirement) && !this.tryAdapt(requirement)) {
        throw new Error(`Runtime requirement not satisfied for ${module.name}: ${requirement.name}`);
      }
    }
  }

  async start(config: Record<string, unknown> = {}): Promise<void> {
    this.ctx.config = { ...this.ctx.config, ...config };
    for (const module of this.startOrder()) {
      this.ensureRuntimeRequirements(module);
      await module.start(this.ctx);
      this.started.push(module);
    }
  }

  async stop(): Promise<void> {
    for (const module of [...this.started].reverse()) await module.stop?.(this.ctx);
    this.started = [];
  }

  async restart(modules: ModuleSpec[], adapters: AdapterSpec[] = []): Promise<void> {
    const config = this.ctx.config;
    await this.stop();
    this.modules = modules;
    this.adapters = adapters;
    this.ctx = new LatticeContext(config);
    await this.start();
  }
}
