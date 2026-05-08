from __future__ import annotations
import argparse, json
from .update_security import UpdateSecurity

def main():
    parser = argparse.ArgumentParser(description="AI Serviter installer production CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sha = sub.add_parser("sha256"); sha.add_argument("path")
    verify = sub.add_parser("verify-sha256"); verify.add_argument("path"); verify.add_argument("expected")
    sign = sub.add_parser("hmac-sign"); sign.add_argument("path"); sign.add_argument("secret")
    args = parser.parse_args()
    sec = UpdateSecurity()
    if args.command == "sha256":
        print(json.dumps({"sha256": sec.sha256(args.path)}, indent=2))
    elif args.command == "verify-sha256":
        print(json.dumps(sec.verify_sha256(args.path, args.expected), indent=2))
    elif args.command == "hmac-sign":
        print(json.dumps({"signature": sec.hmac_sign(args.path, args.secret)}, indent=2))

if __name__ == "__main__":
    main()
