from rankingTool.GUI import GUI

config_file = "config_rest.toml"

def main():
    instance = GUI(config_file)
    instance.show()

if __name__ == "__main__":
    main()
