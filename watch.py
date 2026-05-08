from lattice import HotReloadManager, Kernel, discover


def main():
    modules, adapters = discover("plugins")
    kernel = Kernel(modules, adapters)
    kernel.start()

    app = kernel.ctx.resolve("app", (1, 0))
    app.run()

    manager = HotReloadManager(kernel, "plugins", "plugins")
    manager.watch(interval_seconds=1.0)


if __name__ == "__main__":
    main()
