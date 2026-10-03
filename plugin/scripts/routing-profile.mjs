#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROLES = ["explorer", "worker", "advisor"];
const TIERS = ["mainstay", "crux", "rescue"];
const HEADER = "| Role | `mainstay` | `crux` | `rescue` |";

function parseCell(cell) {
  const dials = new Set();
  for (const candidate of cell.split(" › ")) {
    const match = /^([\w.-]+)(?:\[([\w*, ]+)\])?$/.exec(candidate.trim());
    if (!match) throw new Error(`invalid candidate: ${candidate}`);
    if (match[2] === undefined) {
      dials.add(match[1]);
      continue;
    }
    for (const effort of match[2].split(",")) {
      if (!/^\w+\*?$/.test(effort.trim())) throw new Error(`invalid effort: ${effort}`);
      dials.add(`${match[1]}[${effort.trim().replace("*", "")}]`);
    }
  }
  return [...dials].sort();
}

function parseTable(lines, start) {
  if (!/^\|\s*:?-+:?\s*\|\s*:?-+:?\s*\|\s*:?-+:?\s*\|\s*:?-+:?\s*\|$/.test(lines[start + 1] ?? "")) {
    throw new Error("missing role table separator");
  }
  const table = {};
  for (let index = start + 2; lines[index]?.startsWith("|"); index += 1) {
    const cells = lines[index].split("|").slice(1, -1).map((cell) => cell.trim());
    const role = cells[0];
    if (cells.length !== 4 || !ROLES.includes(role) || table[role]) {
      throw new Error(`invalid or duplicate role row: ${lines[index]}`);
    }
    table[role] = Object.fromEntries(TIERS.map((tier, i) => [tier, parseCell(cells[i + 1])]));
  }
  if (ROLES.some((role) => !table[role])) throw new Error("missing role row");
  return table;
}

export function parseRoutingProfile(markdown) {
  const lines = markdown.split(/\r?\n/).map((line) => line.trim());
  const tables = {};
  let section = null;
  for (let index = 0; index < lines.length; index += 1) {
    if (lines[index] === "## Tiers and choosing inside a cell") section = "claude_code";
    else if (lines[index] === "## Cursor candidates") section = "cursor";
    if (lines[index] !== HEADER) continue;
    if (section === null || tables[section]) throw new Error("unexpected or duplicate role table");
    tables[section] = parseTable(lines, index);
  }
  if (!tables.claude_code || !tables.cursor) throw new Error("missing Claude Code or Cursor role table");
  return tables;
}

export function validateRoute(role, tier, dial, basis, tables) {
  const invalid = (message) => ({ valid: false, message });
  if (!ROLES.includes(role)) return invalid(`role must be one of: ${ROLES.join(", ")}`);
  if (!TIERS.includes(tier)) return invalid(`tier must be one of: ${TIERS.join(", ")}`);
  if (basis !== undefined) {
    if (basis === null || typeof basis !== "object" || Array.isArray(basis)
        || typeof basis.kind !== "string" || typeof basis.ref !== "string" || !basis.ref.trim()) {
      return invalid("basis must be an object with a string kind and a non-empty string ref");
    }
  } else if (tier !== "mainstay") {
    return invalid(`basis is required at ${tier}`);
  }
  const allowed = tier === "mainstay"
    ? ["key-difficulty", "failure", "user-declaration", "low-confidence"]
    : role === "advisor"
      ? (tier === "crux" ? ["low-confidence", "user-declaration"] : ["user-declaration"])
      : (tier === "crux" ? ["key-difficulty", "failure", "user-declaration"] : ["failure", "user-declaration"]);
  if (basis !== undefined && !allowed.includes(basis.kind)) {
    return invalid(`basis.kind must be one of: ${allowed.join(", ")}`);
  }
  const legal = [...new Set([
    ...tables.claude_code[role][tier], ...tables.cursor[role][tier],
  ])].sort();
  if (!legal.includes(dial)) return invalid(`dial ${dial} is outside ${role}/${tier}; legal dials: ${legal.join(", ")}`);
  return { valid: true, message: null };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const profilePath = process.argv[3];
  try {
    if (process.argv[2] !== "--dump" || !profilePath || process.argv.length !== 4) {
      throw new Error("usage: routing-profile.mjs --dump <profile-path>");
    }
    process.stdout.write(`${JSON.stringify(parseRoutingProfile(await readFile(profilePath, "utf8")))}\n`);
  } catch (error) {
    process.stderr.write(`routing profile ${profilePath ?? ""}: ${error.message}\n`);
    process.exitCode = 1;
  }
}
