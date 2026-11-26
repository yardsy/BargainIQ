"""Build an explicit public artifact without publishing source files or credentials."""
from pathlib import Path
from shutil import copy2

def main():
    root=Path(__file__).resolve().parent
    output=root/"public"
    output.mkdir(exist_ok=True)
    for name in ("index.html","account.html","about.html","guides.html","methodology.html","engagement.js","stock.json"):
        copy2(root/name,output/name)
    for name in ("retail.json","history.json","commission-factory-237c1dd364344b708a80b3ce2251b3b7.html"):
        if (root/name).is_file():
            copy2(root/name,output/name)
    from editorial import build_guides
    build_guides(root/"guides.html", output)
    from launch_seo import prepare_beta
    prepare_beta(output)
    (output/"_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  X-Robots-Tag: noindex, nofollow\n  Referrer-Policy: no-referrer\n  X-Frame-Options: DENY\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n", encoding="utf-8")
    print("Prepared public website.")

if __name__=="__main__":
    main()
