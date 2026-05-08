from lattice import Kernel, discover


def main():
    modules, adapters = discover("plugins")
    kernel = Kernel(modules, adapters)
    kernel.start({"project_root": "."})

    app = kernel.ctx.resolve("app", (1, 0))
    app.run()

    serviter = kernel.ctx.resolve("ai_serviter", (1, 0))
    print("[ai-serviter] summary:", serviter.analyze())

    kernel.stop()


if __name__ == "__main__":
    main()
