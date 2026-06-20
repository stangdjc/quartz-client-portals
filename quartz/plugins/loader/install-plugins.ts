#!/usr/bin/env node
import fs from "fs"
import path from "path"
import YAML from "yaml"
import { installPlugins, parsePluginSource } from "./gitLoader.js"
import type { PluginJsonEntry, QuartzPluginsJson } from "./types.js"

function loadEnabledPluginSources(cwd: string) {
  const configPath = path.join(cwd, "quartz.config.yaml")
  const raw = fs.readFileSync(configPath, "utf-8")
  const parsed = YAML.parse(raw) as QuartzPluginsJson | null
  const plugins: PluginJsonEntry[] = Array.isArray(parsed?.plugins) ? parsed.plugins : []

  return plugins.filter((entry) => entry?.enabled).map((entry) => parsePluginSource(entry.source))
}

async function main() {
  const externalPlugins = loadEnabledPluginSources(process.cwd())

  if (externalPlugins.length === 0) {
    console.log("No enabled plugins to install.")
    return
  }

  console.log(`Installing ${externalPlugins.length} enabled plugin(s) from quartz.config.yaml...`)

  const installed = await installPlugins(externalPlugins, { verbose: true })

  if (installed.size === externalPlugins.length) {
    console.log("✓ All plugins installed successfully")
  } else {
    console.error(`✗ Only ${installed.size}/${externalPlugins.length} plugins installed`)
    process.exit(1)
  }
}

main().catch((err) => {
  console.error("Failed to install plugins:", err)
  process.exit(1)
})
