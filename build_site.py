"""Build an explicit public artifact without publishing source files or credentials."""
from pathlib import Path
from shutil import copy2

def main():
    root=Path(__file__).resolve().parent
    output=root/"public"
    output.mkdir(exist_ok=True)
    for name in ("index.html","account.html","about.html","guides.html","stock.json"):
        copy2(root/name,output/name)
    for name in ("retail.json","history.json","commission-factory-237c1dd364344b708a80b3ce2251b3b7.html"):
        if (root/name).is_file():
            copy2(root/name,output/name)
    print("Prepared public website.")

if __name__=="__main__":
    main()
