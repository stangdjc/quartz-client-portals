const normalizeList = (value) => {
  if (Array.isArray(value)) {
    return value
      .flatMap((item) => (typeof item === "string" ? item.split(",") : []))
      .map((item) => item.trim())
      .filter(Boolean)
  }

  if (typeof value === "string") {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)
  }

  return []
}

const normalizeSlug = (value) => String(value ?? "").replace(/^\/+|\/+$/g, "")

const matchesClientTag = (frontmatter, clientTag) => {
  if (!clientTag) {
    return false
  }

  const tags = normalizeList(frontmatter?.tags)
  const explicitClientFields = normalizeList([
    frontmatter?.client,
    frontmatter?.clientTag,
    frontmatter?.clientPortal,
  ])

  return tags.includes(clientTag) || explicitClientFields.includes(clientTag)
}

export default function ClientPortalFilter(options = {}) {
  const configuredClientTag =
    options.clientTag ?? process.env.QUARTZ_CLIENT_TAG ?? "client/template"
  const allowUnscopedSlugs = new Set(
    normalizeList(options.allowUnscopedSlugs ?? ["index"]).map(normalizeSlug),
  )

  return {
    name: "ClientPortalFilter",
    shouldPublish(_ctx, [_tree, vfile]) {
      const slug = normalizeSlug(vfile?.data?.slug)
      if (allowUnscopedSlugs.has(slug)) {
        return true
      }

      const frontmatter = vfile?.data?.frontmatter ?? {}
      return matchesClientTag(frontmatter, configuredClientTag)
    },
  }
}

export const plugin = ClientPortalFilter
