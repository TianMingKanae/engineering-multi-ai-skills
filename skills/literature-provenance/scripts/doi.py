"""Registry-backed DOI identity check, machine-generated BibTeX and explicit venue gate."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

HOSTS = {"doi.org", "api.crossref.org", "data.crosscite.org", "api.datacite.org", "citation.doi.org", "data.medra.org"}


def normalize_doi(value):
    if not isinstance(value, str):
        raise ValueError("DOI must be a string")
    value = value.strip()
    if value.lower().startswith("doi:"):
        value = value[4:].strip()
    if value.lower().startswith("https://"):
        parsed = urlsplit(value)
        if parsed.hostname not in {"doi.org", "dx.doi.org"} or parsed.query or parsed.fragment or parsed.username or parsed.port not in {None, 443}:
            raise ValueError("Use a DOI or an unambiguous DOI resolver URL")
        value = unquote(parsed.path.lstrip("/"))
    if not re.fullmatch(r"10\.\d{4,9}/\S+", value):
        raise ValueError("Invalid supported DOI syntax")
    return value.lower()


def title_key(value):
    value = html.unescape(unicodedata.normalize("NFKC", value)).casefold()
    return "".join(c for c in value if c.isalnum())


class RegistryRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != "https" or parsed.hostname not in HOSTS or parsed.username or parsed.port not in {None, 443}:
            raise ValueError("Unsupported DOI registry redirect; review manually")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(doi, accept):
    url = "https://doi.org/" + quote(doi, safe="/")
    request = Request(url, headers={"Accept": accept, "User-Agent": "engineering-multi-ai-skills DOI verifier"})
    with build_opener(RegistryRedirect()).open(request, timeout=20) as response:
        raw = response.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("DOI response exceeds limit")
        return raw, response.geturl()


def bib_field(text, name):
    match = re.search(r"(?:^|[,\n])\s*" + re.escape(name) + r"\s*=\s*([\{\"])", text, re.I)
    if not match:
        raise ValueError(f"Registry BibTeX missing {name}")
    start, opening = match.end(), match[1]
    depth, escaped = 1, False
    for pos in range(start, len(text)):
        char = text[pos]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if opening == '"' and char == '"':
            return text[start:pos]
        if opening == "{":
            depth += (char == "{") - (char == "}")
            if depth == 0:
                return text[start:pos]
    raise ValueError("Unterminated registry BibTeX field")


def venue_gate(metadata, policy):
    if not isinstance(policy, dict) or not isinstance(policy.get("venues", []), list) or not isinstance(policy.get("allowed_tiers", []), list):
        raise ValueError("Venue policy must contain venue and allowed-tier arrays")
    if not all(isinstance(t, str) for t in policy.get("allowed_tiers", [])):
        raise ValueError("Allowed tiers must be strings")
    for entry in policy.get("venues", []):
        if (not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k] for k in ("name", "type", "tier"))
                or not isinstance(entry.get("issn", []), list) or not all(isinstance(i, str) for i in entry.get("issn", []))):
            raise ValueError("Malformed venue policy entry")
    kind = metadata.get("type", "")
    names = metadata.get("container-title", [])
    if isinstance(names, str):
        names = [names]
    issns = metadata.get("ISSN", [])
    if isinstance(issns, str):
        issns = [issns]
    if kind in {"posted-content", "preprint"} or any(str(metadata.get(k, "")).casefold() == "preprint" for k in ("genre", "subtype")):
        tier = "preprint"
    else:
        matches = []
        for entry in policy.get("venues", []):
            # If identifiers are specified, require one; title-only matches are explicitly weaker policy.
            identifier_ok = not entry.get("issn") or bool(set(entry["issn"]) & set(issns))
            if identifier_ok and entry.get("type") == kind and any(title_key(n) == title_key(entry["name"]) for n in names):
                matches.append(entry["tier"])
        if len(set(matches)) > 1:
            raise ValueError("Conflicting venue policy")
        tier = matches[0] if matches else "unclassified"
    return {"tier": tier, "approved": tier in policy.get("allowed_tiers", []), "type": kind}


def verify(doi, expected_title, policy, retrieve=fetch):
    doi = normalize_doi(doi)
    if not title_key(expected_title):
        raise ValueError("Expected title must be supplied independently")
    raw, metadata_url = retrieve(doi, "application/vnd.citationstyles.csl+json")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("DOI metadata must be one object")
    title = data.get("title", "")
    if not isinstance(title, str) or normalize_doi(data.get("DOI", "")) != doi or title_key(title) != title_key(expected_title):
        raise ValueError("DOI/title identity mismatch")
    bib, bib_url = retrieve(doi, "application/x-bibtex")
    text = bib.decode("utf-8")
    if len(re.findall(r"@\w+\s*\{", text)) != 1 or normalize_doi(bib_field(text, "doi")) != doi:
        raise ValueError("BibTeX DOI/entry mismatch")
    if title_key(bib_field(text, "title")) != title_key(title):
        raise ValueError("BibTeX title differs from metadata; manual review required")
    record = dict(doi=doi, title=title, gate=venue_gate(data, policy), metadata_url=metadata_url, bibtex_url=bib_url,
                  metadata_sha256=hashlib.sha256(raw).hexdigest(), bibtex_sha256=hashlib.sha256(bib).hexdigest(),
                  policy_sha256=hashlib.sha256(json.dumps(policy, sort_keys=True).encode()).hexdigest())
    return record, raw, bib


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("doi")
    p.add_argument("--expected-title", required=True)
    p.add_argument("--policy", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True, help="New approved-record directory; never overwrite")
    args = p.parse_args()
    try:
        record, raw, bib = verify(args.doi, args.expected_title, json.loads(args.policy.read_text(encoding="utf-8")))
        if not record["gate"]["approved"]:
            print(json.dumps(record))
            return 2
        args.out.mkdir(parents=True, exist_ok=False)
        (args.out / "metadata.json").write_bytes(raw)
        (args.out / "citation.bib").write_bytes(bib)
        (args.out / "provenance.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(record))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
