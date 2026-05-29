import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import cogneeGraphExport from "./cognee-graph.json";
import "./styles.css";

type FrontmatterValue = string | string[];

type WikiPage = {
  path: string;
  title: string;
  type: string;
  status: string;
  tags: string[];
  aliases: string[];
  related: string[];
  sources: string[];
  confidence: string;
  body: string;
  raw: string;
};

type SearchHit = {
  page: WikiPage;
  score: number;
};

type GraphNode = {
  id: string;
  page: WikiPage;
  x: number;
  y: number;
  active: boolean;
};

type GraphEdge = {
  from: string;
  to: string;
  kind: "link" | "backlink" | "source" | "tag";
};

type PageTab = "article" | "ask" | "graph" | "sources" | "related";

type CogneeNode = {
  id: string;
  label: string;
  type: string;
  description?: string;
  sourceTask?: string;
  sourcePipeline?: string;
};

type CogneeEdge = {
  source: string;
  target: string;
  label: string;
  relationship?: string;
};

type CogneeGraphExport = {
  kind: string;
  dataset: string;
  datasetId: string;
  exportedAt: string;
  source: string;
  nodeCount: number;
  edgeCount: number;
  nodes: CogneeNode[];
  edges: CogneeEdge[];
  error?: string;
};

type CogneeNodeGroup = "anchor" | "source" | "entity" | "type" | "memory";

type CogneeVisualNode = CogneeNode & {
  x: number;
  y: number;
  active: boolean;
  wikiPath?: string;
  displayLabel: string;
  detail: string;
  group: CogneeNodeGroup;
  score: number;
};

type CogneeVisualEdge = CogneeEdge & {
  sourceNode: CogneeVisualNode;
  targetNode: CogneeVisualNode;
  displayLabel: string;
};

type CogneeRelationRow = {
  id: string;
  source: CogneeVisualNode;
  target: CogneeVisualNode;
  label: string;
};

type CogneeGraphResult = {
  nodes: CogneeVisualNode[];
  edges: CogneeVisualEdge[];
  anchorCount: number;
  hiddenCount: number;
  relationRows: CogneeRelationRow[];
};

const cogneeGraph = cogneeGraphExport as CogneeGraphExport;

const modules = import.meta.glob<string>("../wiki/**/*.md", {
  query: "?raw",
  import: "default",
  eager: true
});

const pages = Object.entries(modules)
  .map(([path, raw]) => parsePage(path.replace("../wiki/", ""), raw))
  .sort((a, b) => a.title.localeCompare(b.title));

const pageByPath = new Map(pages.map((page) => [page.path, page]));
const defaultPath = pageByPath.has("index.md") ? "index.md" : pages[0]?.path ?? "";

function parsePage(path: string, raw: string): WikiPage {
  const frontmatter: Record<string, FrontmatterValue> = {};
  let body = raw;

  if (raw.startsWith("---")) {
    const end = raw.indexOf("\n---", 3);
    if (end >= 0) {
      const yaml = raw.slice(3, end).trim();
      body = raw.slice(end + 4).trim();
      Object.assign(frontmatter, parseFrontmatter(yaml));
    }
  }

  return {
    path,
    title: stringValue(frontmatter.title, titleFromPath(path)),
    type: stringValue(frontmatter.type, "page"),
    status: stringValue(frontmatter.status, "draft"),
    tags: arrayValue(frontmatter.tags),
    aliases: arrayValue(frontmatter.aliases),
    related: arrayValue(frontmatter.related),
    sources: arrayValue(frontmatter.sources),
    confidence: stringValue(frontmatter.confidence, "unknown"),
    body,
    raw
  };
}

function parseFrontmatter(yaml: string): Record<string, FrontmatterValue> {
  const result: Record<string, FrontmatterValue> = {};
  const lines = yaml.split(/\r?\n/);
  let currentKey: string | null = null;

  for (const line of lines) {
    const listMatch = line.match(/^\s+-\s+(.*)$/);
    if (listMatch && currentKey) {
      const current = result[currentKey];
      result[currentKey] = Array.isArray(current)
        ? [...current, listMatch[1].trim()]
        : [listMatch[1].trim()];
      continue;
    }

    const keyMatch = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!keyMatch) continue;

    currentKey = keyMatch[1];
    const value = keyMatch[2].trim();
    result[currentKey] = value ? value.replace(/^["']|["']$/g, "") : [];
  }

  return result;
}

function stringValue(value: FrontmatterValue | undefined, fallback: string): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function arrayValue(value: FrontmatterValue | undefined): string[] {
  if (Array.isArray(value)) return value.filter(Boolean);
  if (typeof value === "string" && value.length > 0) return [value];
  return [];
}

function titleFromPath(path: string): string {
  return path
    .replace(/\.md$/, "")
    .split("/")
    .pop()
    ?.replace(/-/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase()) ?? path;
}

function resolvePath(currentPath: string, href: string): string {
  if (/^(https?:|mailto:|#)/.test(href)) return href;
  const baseParts = currentPath.split("/").slice(0, -1);
  const parts = [...baseParts, ...href.split("/")];
  const resolved: string[] = [];

  for (const part of parts) {
    if (!part || part === ".") continue;
    if (part === "..") {
      resolved.pop();
    } else {
      resolved.push(part);
    }
  }

  return resolved.join("/");
}

function searchPages(query: string): SearchHit[] {
  const terms = query
    .toLowerCase()
    .split(/\s+/)
    .map((term) => term.trim())
    .filter(Boolean);

  if (terms.length === 0) return [];

  return pages
    .map((page) => {
      const haystack = [
        page.title,
        page.type,
        page.status,
        page.tags.join(" "),
        page.aliases.join(" "),
        page.sources.join(" "),
        page.body
      ]
        .join(" ")
        .toLowerCase();

      const score = terms.reduce((sum, term) => {
        if (page.title.toLowerCase().includes(term)) return sum + 10;
        if (page.tags.some((tag) => tag.toLowerCase().includes(term))) return sum + 5;
        return haystack.includes(term) ? sum + 1 : sum;
      }, 0);

      return { page, score };
    })
    .filter((hit) => hit.score > 0)
    .sort((a, b) => b.score - a.score || a.page.title.localeCompare(b.page.title));
}

function backlinksFor(path: string): WikiPage[] {
  return pages.filter((page) => {
    if (page.path === path) return false;
    const links = [...page.related, ...extractMarkdownLinks(page.body)];
    return links.some((href) => resolvePath(page.path, href) === path);
  });
}

function extractMarkdownLinks(markdown: string): string[] {
  return [...markdown.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)].map((match) => match[1]);
}

function graphForPage(currentPage: WikiPage): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const nodeIds = new Set<string>([currentPage.path]);
  const edges: GraphEdge[] = [];

  const addEdge = (from: string, to: string, kind: GraphEdge["kind"]) => {
    if (from === to || !pageByPath.has(from) || !pageByPath.has(to)) return;
    const key = `${from}->${to}:${kind}`;
    if (edges.some((edge) => `${edge.from}->${edge.to}:${edge.kind}` === key)) return;
    nodeIds.add(from);
    nodeIds.add(to);
    edges.push({ from, to, kind });
  };

  [...currentPage.related, ...extractMarkdownLinks(currentPage.body)].forEach((href) => {
    const resolved = resolvePath(currentPage.path, href);
    if (pageByPath.has(resolved)) addEdge(currentPage.path, resolved, "link");
  });

  backlinksFor(currentPage.path).forEach((page) => addEdge(page.path, currentPage.path, "backlink"));

  const sharedSourcePages = pages
    .filter((page) => page.path !== currentPage.path)
    .filter((page) => page.sources.some((source) => currentPage.sources.includes(source)))
    .slice(0, 5);
  sharedSourcePages.forEach((page) => addEdge(currentPage.path, page.path, "source"));

  const sharedTagPages = pages
    .filter((page) => page.path !== currentPage.path && !nodeIds.has(page.path))
    .filter((page) => page.tags.some((tag) => currentPage.tags.includes(tag)))
    .slice(0, 5);
  sharedTagPages.forEach((page) => addEdge(currentPage.path, page.path, "tag"));

  const selected = [...nodeIds].slice(0, 18);
  const outer = selected.filter((path) => path !== currentPage.path);
  const center = { x: 280, y: 170 };
  const radiusX = 210;
  const radiusY = 118;

  const nodes = selected.map((path) => {
    const page = pageByPath.get(path)!;
    if (path === currentPage.path) {
      return { id: path, page, x: center.x, y: center.y, active: true };
    }
    const index = outer.indexOf(path);
    const angle = outer.length <= 1 ? 0 : (Math.PI * 2 * index) / outer.length - Math.PI / 2;
    return {
      id: path,
      page,
      x: center.x + Math.cos(angle) * radiusX,
      y: center.y + Math.sin(angle) * radiusY,
      active: false
    };
  });

  return {
    nodes,
    edges: edges.filter((edge) => selected.includes(edge.from) && selected.includes(edge.to))
  };
}

function cogneeGraphForPage(
  currentPage: WikiPage,
  maxNodes: number
): CogneeGraphResult {
  if (!cogneeGraph.nodes.length) {
    return { nodes: [], edges: [], anchorCount: 0, hiddenCount: 0, relationRows: [] };
  }

  const nodesById = new Map(cogneeGraph.nodes.map((node) => [node.id, node]));
  const pageTerms = pageSearchTerms(currentPage);
  const scoredNodes = cogneeGraph.nodes
    .map((node) => ({ node, score: cogneeNodeScore(node, pageTerms, currentPage.sources) }))
    .sort((a, b) => b.score - a.score || cogneeNodeDisplayLabel(a.node).localeCompare(cogneeNodeDisplayLabel(b.node)));

  let anchorIds = uniqueScoredNodeIds(
    scoredNodes.filter((item) => item.score > 0),
    maxNodes > 45 ? 8 : 4
  );

  if (!anchorIds.length) {
    anchorIds = highestDegreeNodeIds(maxNodes > 45 ? 8 : 4);
  }

  const adjacency = new Map<string, CogneeEdge[]>();
  for (const edge of cogneeGraph.edges) {
    if (!nodesById.has(edge.source) || !nodesById.has(edge.target)) continue;
    adjacency.set(edge.source, [...(adjacency.get(edge.source) ?? []), edge]);
    adjacency.set(edge.target, [...(adjacency.get(edge.target) ?? []), edge]);
  }

  const selected = new Set<string>();
  addNodeIds(selected, anchorIds, maxNodes);

  const firstHop = rankCogneeNeighbors(anchorIds, selected, adjacency, nodesById, pageTerms, currentPage.sources);
  const firstHopLimit = Math.max(anchorIds.length, Math.floor(maxNodes * 0.72));
  addNodeIds(selected, uniqueScoredNodeIds(firstHop, firstHopLimit), firstHopLimit);

  const secondHopSeeds = [...selected].filter((id) => {
    const node = nodesById.get(id);
    return node?.type === "Entity";
  });
  const semanticHop = rankCogneeNeighbors(secondHopSeeds, selected, adjacency, nodesById, pageTerms, currentPage.sources)
    .filter((item) => relationshipWeight(item.edgeLabel) >= 16);
  addNodeIds(selected, uniqueScoredNodeIds(semanticHop, maxNodes), maxNodes);

  const selectedNodes = [...selected]
    .map((id) => nodesById.get(id))
    .filter((node): node is CogneeNode => Boolean(node));
  const anchorSet = new Set(anchorIds);
  const selectedScores = new Map(scoredNodes.map((item) => [item.node.id, item.score]));
  const visualSeeds = selectedNodes.map((node) => ({
    ...node,
    active: anchorSet.has(node.id),
    wikiPath: wikiPathForCogneeNode(node),
    displayLabel: cogneeNodeDisplayLabel(node),
    detail: cogneeNodeDetail(node),
    group: cogneeNodeGroup(node, anchorSet),
    score: selectedScores.get(node.id) ?? 0,
  }));
  const positions = positionCogneeNodes(visualSeeds, maxNodes > 45);

  const visualNodes = visualSeeds.map((node) => ({
    ...node,
    ...positions.get(node.id)!,
  }));
  const visualById = new Map(visualNodes.map((node) => [node.id, node]));

  const visualEdges = cogneeGraph.edges
    .filter((edge) => visualById.has(edge.source) && visualById.has(edge.target))
    .sort((a, b) => relationshipWeight(b.label) - relationshipWeight(a.label))
    .map((edge) => ({
      ...edge,
      sourceNode: visualById.get(edge.source)!,
      targetNode: visualById.get(edge.target)!,
      displayLabel: formatRelationship(edge.label),
    }));

  return {
    nodes: visualNodes,
    edges: visualEdges,
    anchorCount: anchorIds.length,
    hiddenCount: Math.max(0, cogneeGraph.nodes.length - visualNodes.length),
    relationRows: relationRowsForEdges(visualEdges, maxNodes > 45 ? 18 : 8),
  };
}

function pageSearchTerms(page: WikiPage): string[] {
  return [
    page.path,
    page.path.replace(/\.md$/, "").split("/").pop() ?? "",
    page.title,
    ...page.aliases,
    ...page.sources,
    ...page.tags,
  ]
    .flatMap((value) => value.toLowerCase().split(/[^a-z0-9.+-]+/))
    .map((value) => value.trim())
    .filter((value, index, all) => value.length >= 3 && all.indexOf(value) === index);
}

function cogneeNodeScore(node: CogneeNode, terms: string[], sources: string[]): number {
  const haystack = `${node.label} ${node.description ?? ""}`.toLowerCase();
  let score = 0;

  for (const source of sources) {
    if (source && haystack.includes(source.toLowerCase())) score += 60;
  }

  for (const term of terms) {
    if (haystack.includes(term)) score += term.length > 8 ? 10 : 5;
  }

  if (node.type === "TextDocument" || node.type === "TextSummary") score += 4;
  if (node.type === "DocumentChunk") score += 2;
  if (node.type === "Entity") score += 3;
  return score;
}

function rankCogneeNeighbors(
  seedIds: string[],
  selected: Set<string>,
  adjacency: Map<string, CogneeEdge[]>,
  nodesById: Map<string, CogneeNode>,
  terms: string[],
  sources: string[]
): Array<{ node: CogneeNode; score: number; edgeLabel: string }> {
  const best = new Map<string, { node: CogneeNode; score: number; edgeLabel: string }>();

  for (const seedId of seedIds) {
    for (const edge of adjacency.get(seedId) ?? []) {
      const otherId = edge.source === seedId ? edge.target : edge.source;
      if (selected.has(otherId)) continue;
      const node = nodesById.get(otherId);
      if (!node) continue;

      const score =
        cogneeNodeScore(node, terms, sources) +
        relationshipWeight(edge.label) +
        cogneeNodeTypeWeight(node);
      const previous = best.get(otherId);
      if (!previous || score > previous.score) {
        best.set(otherId, { node, score, edgeLabel: edge.label });
      }
    }
  }

  return [...best.values()].sort(
    (a, b) => b.score - a.score || cogneeNodeDisplayLabel(a.node).localeCompare(cogneeNodeDisplayLabel(b.node))
  );
}

function addNodeIds(selected: Set<string>, ids: string[], maxNodes: number) {
  for (const id of ids) {
    if (selected.size >= maxNodes) return;
    selected.add(id);
  }
}

function uniqueScoredNodeIds<T extends { node: CogneeNode; score: number }>(
  scored: T[],
  limit: number
): string[] {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const item of scored) {
    if (item.score <= 0) continue;
    const key = cogneeNodeDedupeKey(item.node);
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(item.node.id);
    if (result.length >= limit) break;
  }

  return result;
}

function cogneeNodeDedupeKey(node: CogneeNode): string {
  const sourceId = metadataValue(node, "source_id");
  if (sourceId && isCogneeSourceNode(node)) return `${node.type}:${sourceId}`;
  return `${node.type}:${cogneeNodeDisplayLabel(node).toLowerCase()}`;
}

function highestDegreeNodeIds(limit: number): string[] {
  const degree = new Map<string, number>();
  for (const edge of cogneeGraph.edges) {
    degree.set(edge.source, (degree.get(edge.source) ?? 0) + 1);
    degree.set(edge.target, (degree.get(edge.target) ?? 0) + 1);
  }
  return [...degree.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([id]) => id);
}

function positionCogneeNodes(
  nodes: Array<CogneeNode & { group: CogneeNodeGroup; active: boolean }>,
  large: boolean
): Map<string, { x: number; y: number }> {
  const width = large ? 760 : 560;
  const height = large ? 500 : 340;
  const result = new Map<string, { x: number; y: number }>();

  const groups: Record<CogneeNodeGroup, Array<CogneeNode & { group: CogneeNodeGroup; active: boolean }>> = {
    anchor: nodes.filter((node) => node.group === "anchor"),
    source: nodes.filter((node) => node.group === "source"),
    entity: nodes.filter((node) => node.group === "entity"),
    type: nodes.filter((node) => node.group === "type"),
    memory: nodes.filter((node) => node.group === "memory"),
  };

  positionVertical(groups.source, { x: large ? 126 : 90, y: height / 2 }, large ? 54 : 38, result);
  positionVertical(groups.anchor, { x: large ? 286 : 205, y: height / 2 }, large ? 58 : 40, result);
  positionRing(groups.entity, { x: large ? 520 : 382, y: large ? 235 : 160 }, large ? 160 : 108, large ? 132 : 86, result);
  positionRing(groups.type, { x: large ? 550 : 400, y: large ? 405 : 282 }, large ? 128 : 86, large ? 52 : 34, result);
  positionRing(groups.memory, { x: width / 2, y: large ? 92 : 66 }, large ? 210 : 150, large ? 48 : 32, result);

  return result;
}

function positionVertical(
  nodes: CogneeNode[],
  center: { x: number; y: number },
  gap: number,
  result: Map<string, { x: number; y: number }>
) {
  const start = center.y - ((nodes.length - 1) * gap) / 2;
  nodes.forEach((node, index) => result.set(node.id, { x: center.x, y: start + index * gap }));
}

function positionRing(
  nodes: CogneeNode[],
  center: { x: number; y: number },
  radiusX: number,
  radiusY: number,
  result: Map<string, { x: number; y: number }>
) {
  nodes.forEach((node, index) => {
    if (nodes.length === 1) {
      result.set(node.id, center);
      return;
    }
    const angle = (Math.PI * 2 * index) / nodes.length - Math.PI / 2;
    result.set(node.id, {
      x: center.x + Math.cos(angle) * radiusX,
      y: center.y + Math.sin(angle) * radiusY,
    });
  });
}

function cogneeNodeGroup(node: CogneeNode, anchors: Set<string>): CogneeNodeGroup {
  if (anchors.has(node.id)) return "anchor";
  if (isCogneeSourceNode(node)) return "source";
  if (node.type === "Entity") return "entity";
  if (node.type === "EntityType") return "type";
  return "memory";
}

function cogneeNodeTypeWeight(node: CogneeNode): number {
  if (node.type === "Entity") return 18;
  if (node.type === "EntityType") return 12;
  if (node.type === "TextSummary") return 7;
  if (node.type === "TextDocument") return 5;
  if (node.type === "DocumentChunk") return 4;
  return 6;
}

function relationshipWeight(label: string): number {
  if (label === "is_a") return 24;
  if (label === "contains") return 18;
  if (label.includes("related")) return 22;
  if (label.includes("discusses") || label.includes("mentions") || label.includes("references")) return 20;
  if (label.includes("authored") || label.includes("implemented") || label.includes("uses")) return 19;
  if (label.includes("source") || label.includes("url")) return 10;
  return 14;
}

function isCogneeSourceNode(node: CogneeNode): boolean {
  return node.type === "DocumentChunk" || node.type === "TextDocument" || node.type === "TextSummary";
}

function cogneeNodeDisplayLabel(node: CogneeNode): string {
  const rawLabel = cleanCogneeText(node.label);
  const entityName = metadataValue(node, "entity_name");
  const sourceId = metadataValue(node, "source_id");
  const title = metadataValue(node, "title");

  if (looksGeneratedId(rawLabel)) {
    return cleanCogneeText(entityName || sourceId || title || node.type);
  }

  return cleanCogneeText(rawLabel);
}

function cogneeNodeDetail(node: CogneeNode): string {
  const sourceId = metadataValue(node, "source_id");
  const kind = metadataValue(node, "kind");
  if (sourceId && kind) return `${node.type} - ${sourceId} - ${kind}`;
  if (sourceId) return `${node.type} - ${sourceId}`;
  return node.type;
}

function metadataValue(node: CogneeNode, key: string): string {
  const description = node.description ?? "";
  const pattern = new RegExp(`${key}:\\s*(.+?)(?=\\s+[a-z_]+:|;|$)`, "i");
  const match = description.match(pattern);
  return match ? cleanCogneeText(match[1]) : "";
}

function cleanCogneeText(value: string): string {
  return value
    .replace(/^wiki\//, "")
    .replace(/[`"]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function looksGeneratedId(value: string): boolean {
  return /^[0-9a-f]{32}$/i.test(value) || /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}/i.test(value);
}

function relationRowsForEdges(edges: CogneeVisualEdge[], limit: number): CogneeRelationRow[] {
  const seen = new Set<string>();
  const rows: CogneeRelationRow[] = [];

  for (const edge of edges) {
    const key = `${edge.sourceNode.displayLabel}->${edge.displayLabel}->${edge.targetNode.displayLabel}`;
    if (seen.has(key)) continue;
    seen.add(key);
    rows.push({
      id: key,
      source: edge.sourceNode,
      target: edge.targetNode,
      label: edge.displayLabel,
    });
    if (rows.length >= limit) break;
  }

  return rows;
}

function wikiPathForCogneeNode(node: CogneeNode): string | undefined {
  const label = cleanCogneeText(node.label);
  if (pageByPath.has(label)) return label;
  if (pageByPath.has(`${label}.md`)) return `${label}.md`;
  const normalized = label.toLowerCase();
  return pages.find((page) => page.title.toLowerCase() === normalized)?.path;
}

function App() {
  const [currentPath, setCurrentPath] = useState(readHashPath());
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState<PageTab>("article");
  const [showDarioPopup, setShowDarioPopup] = useState(true);

  useEffect(() => {
    const onHashChange = () => setCurrentPath(readHashPath());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    setActiveTab("article");
    window.scrollTo({ top: 0 });
  }, [currentPath]);

  const currentPage = pageByPath.get(currentPath) ?? pageByPath.get(defaultPath);
  const hits = useMemo(() => searchPages(query), [query]);
  const groupedPages = useMemo(() => groupByType(pages), []);

  if (!currentPage) {
    return <main className="empty">No wiki pages found.</main>;
  }

  const backlinks = backlinksFor(currentPage.path);

  return (
    <div className="app-shell">
      {showDarioPopup ? (
        <div className="dario-popup" role="dialog" aria-modal="true" aria-labelledby="dario-popup-title">
          <div className="dario-popup-box">
            <button
              className="dario-popup-close"
              type="button"
              aria-label="Close"
              onClick={() => setShowDarioPopup(false)}
            >
              x
            </button>
            <img src="/dario_img.png" alt="Dario" />
            <div className="dario-popup-text">
              <h2 id="dario-popup-title">Notice</h2>
              <p>
                Karpathy now works for Dario, but this project was created with Codex.
                <br />
                No shade.
              </p>
            </div>
          </div>
        </div>
      ) : null}

      <aside className="sidebar" aria-label="Wiki navigation">
        <a className="brand" href={`#/${defaultPath}`} onClick={() => setQuery("")}>
          <span className="brand-mark">K</span>
          <span>
            <strong>Karpathy Wiki</strong>
            <small>Cognee memory edition</small>
          </span>
        </a>

        <label className="search-label" htmlFor="wiki-search">
          Search
        </label>
        <input
          id="wiki-search"
          className="search-input"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="concept, project, source..."
        />

        {query ? (
          <nav className="nav-section" aria-label="Search results">
            <h2>Results</h2>
            {hits.length === 0 ? (
              <p className="muted">No pages matched.</p>
            ) : (
              hits.slice(0, 12).map((hit) => (
                <PageLink
                  key={hit.page.path}
                  page={hit.page}
                  active={hit.page.path === currentPage.path}
                />
              ))
            )}
          </nav>
        ) : (
          Object.entries(groupedPages).map(([type, group]) => (
            <nav className="nav-section" aria-label={type} key={type}>
              <h2>{typeLabel(type)}</h2>
              {group.map((page) => (
                <PageLink
                  key={page.path}
                  page={page}
                  active={page.path === currentPage.path}
                />
              ))}
            </nav>
          ))
        )}
      </aside>

      <main className="content">
        <header className="page-header">
          <div>
            <h1>{currentPage.title}</h1>
            <p className="page-subtitle">From Karpathy Wiki, the Cognee-backed memory encyclopedia</p>
          </div>
        </header>

        <nav className="page-tabs" aria-label="Page sections">
          <TabButton tab="article" activeTab={activeTab} setActiveTab={setActiveTab}>Article</TabButton>
          <TabButton tab="ask" activeTab={activeTab} setActiveTab={setActiveTab}>Ask Cognee</TabButton>
          <TabButton tab="graph" activeTab={activeTab} setActiveTab={setActiveTab}>Graph</TabButton>
          <TabButton tab="sources" activeTab={activeTab} setActiveTab={setActiveTab}>Sources</TabButton>
          <TabButton tab="related" activeTab={activeTab} setActiveTab={setActiveTab}>Related</TabButton>
        </nav>

        <RetroOfficeDecor currentPage={currentPage} activeTab={activeTab} setActiveTab={setActiveTab} />

        {activeTab === "article" ? (
          <div className="page-layout">
            <article className="markdown" id="article-top">
              <Markdown page={currentPage} />
            </article>

            <aside className="info-rail" aria-label="Page facts and graph">
              <PageInfobox currentPage={currentPage} setQuery={setQuery} />
              <KnowledgeGraph currentPage={currentPage} />
            </aside>
          </div>
        ) : null}

        {activeTab === "ask" ? (
          <AskCogneePanel currentPage={currentPage} />
        ) : null}

        {activeTab === "graph" ? (
          <GraphPanel currentPage={currentPage} />
        ) : null}

        {activeTab === "sources" ? (
          <SourcesPanel currentPage={currentPage} />
        ) : null}

        {activeTab === "related" ? (
          <RelatedPanel currentPage={currentPage} backlinks={backlinks} />
        ) : null}
      </main>
    </div>
  );
}

function RetroOfficeDecor({
  currentPage,
  activeTab,
  setActiveTab
}: {
  currentPage: WikiPage;
  activeTab: PageTab;
  setActiveTab: (tab: PageTab) => void;
}) {
  const pageLabel = `${typeLabel(currentPage.type)} file`;
  const assistantLines = retroAssistantLines(currentPage, activeTab);
  const [assistantIndex, setAssistantIndex] = useState(0);

  useEffect(() => {
    setAssistantIndex(0);
  }, [currentPage.path, activeTab]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setAssistantIndex((index) => (index + 1) % assistantLines.length);
    }, 3600);
    return () => window.clearInterval(timer);
  }, [assistantLines.length, currentPage.path, activeTab]);

  const assistantLine = assistantLines[assistantIndex] ?? assistantLines[0];

  return (
    <>
      <section className="office-decor" aria-label="Office-style page art">
        <div className="office-titlebar">
          <span>Karpathy Wiki 2000</span>
          <span className="office-window-buttons" aria-hidden="true">
            <i />
            <i />
            <i />
          </span>
        </div>

        <div className="office-toolbar" aria-hidden="true">
          <span>File</span>
          <span>Edit</span>
          <span>View</span>
          <span>Insert</span>
          <span>Format</span>
          <span>Tools</span>
          <span>Graph</span>
        </div>

        <div className="office-decor-body">
          <div className="wordart-stack">
            <p className="wordart-eyebrow">{pageLabel}</p>
            <p className="wordart-title">{currentPage.title}</p>
          </div>

          <div className="clipart-strip">
            <RetroClip icon="document" label="Sources" delay={0} onClick={() => setActiveTab("sources")} />
            <RetroClip icon="chart" label="Graph" delay={1} onClick={() => setActiveTab("graph")} />
            <RetroClip icon="spark" label="Memory" delay={2} onClick={() => setActiveTab("ask")} />
            <RetroClip icon="nodes" label="Cognee" delay={3} href="https://github.com/topoteretes/cognee" />
          </div>
        </div>
      </section>

      <aside className="office-helper-panel" aria-label="Chaotic wiki helper suggestions">
        <RetroAssistant />
        <div className="helper-bubble-stage">
          <div className="helper-bubble" key={`${currentPage.path}-${activeTab}-${assistantIndex}`}>
            <strong>Wiki Helper</strong>
            <span>{assistantLine}</span>
          </div>
          <div className="helper-bubble-counter" aria-label="Helper message count">
            {assistantIndex + 1}/{assistantLines.length}
          </div>
        </div>
      </aside>
    </>
  );
}

function retroAssistantLines(page: WikiPage, activeTab: PageTab): string[] {
  const suggestions = [
    "Bad idea detected: do not run the delete-everything terminal incantation. Click Sources instead.",
    "Pro tip: rename every folder final_final_v2 for enterprise credibility.",
    "If the graph looks tangled, add a bevel and call it knowledge management.",
    "Ask Cognee twice. If it disagrees, blink slowly and cite the source note.",
    "Install more RAM by opening PowerPoint and believing very hard.",
    "Before touching sudo, make a backup and maybe also a sandwich.",
    "Citation missing? Just stare at the page until a source ID appears.",
    "The Memory button remembers things. I remember 2003 and six toolbars.",
    "To improve latency, close your eyes during loading.",
    "If a claim feels true, punish it with a citation."
  ];
  const seed = hashString(`${page.path}:${activeTab}`);
  const picked = [0, 1, 2].map((offset) => suggestions[(seed + offset * 3) % suggestions.length]);
  return [retroAssistantLine(page, activeTab), ...picked];
}

function retroAssistantLine(page: WikiPage, activeTab: PageTab): string {
  if (activeTab === "ask") return "Ask Cognee, then file the useful answer back into the wiki.";
  if (activeTab === "graph") return "The memory graph is selected from Cognee's exported relationships.";
  if (activeTab === "sources") return "Source IDs are the handles behind the citations.";
  if (activeTab === "related") return "Follow links and backlinks like a 2000s research rabbit hole.";
  if (page.type === "source-note") return "This page is evidence first, synthesis second.";
  if (page.type === "project") return "Project pages connect code, essays, claims, and implementation details.";
  if (page.type === "concept") return "Concept pages collect recurring ideas across Karpathy's work.";
  return "Browse, cite, query, improve, repeat.";
}

function hashString(value: string): number {
  return [...value].reduce((hash, character) => {
    return (hash * 31 + character.charCodeAt(0)) >>> 0;
  }, 7);
}

function RetroClip({
  icon,
  label,
  delay,
  href,
  onClick
}: {
  icon: "document" | "chart" | "spark" | "nodes";
  label: string;
  delay: number;
  href?: string;
  onClick?: () => void;
}) {
  const content = (
    <>
      <svg viewBox="0 0 72 72" role="img" aria-label={label}>
        {icon === "document" ? (
          <>
            <path className="clip-shadow" d="M19 14h28l10 10v38H19z" />
            <path className="clip-paper" d="M15 10h29l11 11v37H15z" />
            <path className="clip-fold" d="M44 10v12h11" />
            <path className="clip-line" d="M22 29h24M22 38h26M22 47h18" />
          </>
        ) : null}
        {icon === "chart" ? (
          <>
            <rect className="clip-panel" x="12" y="16" width="48" height="40" />
            <path className="clip-axis" d="M20 48h32M20 48V24" />
            <rect className="clip-bar red" x="25" y="36" width="6" height="12" />
            <rect className="clip-bar green" x="35" y="29" width="6" height="19" />
            <rect className="clip-bar blue" x="45" y="22" width="6" height="26" />
          </>
        ) : null}
        {icon === "spark" ? (
          <>
            <path className="clip-star star-big" d="M36 8l6 19 19-1-16 11 7 18-16-11-16 11 7-18-16-11 19 1z" />
            <circle className="clip-orbit" cx="36" cy="36" r="24" />
            <circle className="clip-dot one" cx="13" cy="36" r="4" />
            <circle className="clip-dot two" cx="57" cy="29" r="3" />
          </>
        ) : null}
        {icon === "nodes" ? (
          <>
            <path className="clip-network-line" d="M22 44l14-18 16 22M22 44l30 4M36 26l16 22" />
            <circle className="clip-network-node blue" cx="22" cy="44" r="8" />
            <circle className="clip-network-node green" cx="36" cy="26" r="8" />
            <circle className="clip-network-node red" cx="52" cy="48" r="8" />
            <path className="clip-network-spark" d="M16 16l4 8 8 4-8 4-4 8-4-8-8-4 8-4z" />
          </>
        ) : null}
      </svg>
      <span>{label}</span>
    </>
  );

  if (href) {
    return (
      <a
        className="clipart-card"
        href={href}
        style={{ "--clip-delay": `${delay * 120}ms` } as React.CSSProperties}
      >
        {content}
      </a>
    );
  }

  return (
    <button
      className="clipart-card"
      type="button"
      onClick={onClick}
      style={{ "--clip-delay": `${delay * 120}ms` } as React.CSSProperties}
    >
      {content}
    </button>
  );
}

function RetroAssistant() {
  return (
    <svg className="retro-assistant" viewBox="0 0 92 92" role="img" aria-label="Animated wiki helper">
      <path className="assistant-shadow" d="M24 80c13 7 39 7 48 0" />
      <path className="assistant-wire outer" d="M58 19c17 8 20 29 8 43-11 13-33 10-41-3-8-14 1-34 17-35 13-1 24 11 21 24-3 12-18 18-29 11-8-6-10-18-3-26" />
      <path className="assistant-wire inner" d="M42 32c8-1 15 6 14 14-1 8-10 13-17 9-6-3-8-11-4-16" />
      <circle className="assistant-eye left" cx="40" cy="35" r="5" />
      <circle className="assistant-eye right" cx="58" cy="39" r="3" />
      <circle className="assistant-pupil left" cx="42" cy="36" r="1.8" />
      <circle className="assistant-pupil right" cx="57" cy="38" r="1.3" />
      <path className="assistant-smile" d="M42 52c5 6 16 3 20-4" />
      <path className="assistant-hand" d="M65 50l12-8M73 42l8 2M73 42l3-8" />
      <path className="assistant-sparkline" d="M20 23l4 6 7-9 5 11 5-5" />
    </svg>
  );
}

function readHashPath(): string {
  const value = window.location.hash.replace(/^#\/?/, "");
  return pageByPath.has(value) ? value : defaultPath;
}

function groupByType(items: WikiPage[]): Record<string, WikiPage[]> {
  const priority = ["overview", "person", "timeline", "concept", "project", "source-note", "log"];
  const groups = items.reduce<Record<string, WikiPage[]>>((acc, page) => {
    acc[page.type] = [...(acc[page.type] ?? []), page];
    return acc;
  }, {});

  return Object.fromEntries(
    Object.entries(groups).sort(
      ([a], [b]) => priority.indexOf(a) - priority.indexOf(b)
    )
  );
}

function typeLabel(type: string): string {
  return type
    .split("-")
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join(" ");
}

function TabButton({
  tab,
  activeTab,
  setActiveTab,
  children
}: {
  tab: PageTab;
  activeTab: PageTab;
  setActiveTab: (tab: PageTab) => void;
  children: React.ReactNode;
}) {
  return (
    <button
      className={activeTab === tab ? "selected" : ""}
      type="button"
      aria-pressed={activeTab === tab}
      onClick={() => setActiveTab(tab)}
    >
      {children}
    </button>
  );
}

function PageLink({ page, active }: { page: WikiPage; active: boolean }) {
  return (
    <a className={`page-link ${active ? "active" : ""}`} href={`#/${page.path}`}>
      <span>{page.title}</span>
      <small>{page.type}</small>
    </a>
  );
}

function PageInfobox({
  currentPage,
  setQuery
}: {
  currentPage: WikiPage;
  setQuery: (query: string) => void;
}) {
  return (
    <section className="infobox">
      <h2>{currentPage.title}</h2>
      <Meta label="Type" value={currentPage.type} />
      <Meta label="Status" value={currentPage.status} />
      <Meta label="Confidence" value={currentPage.confidence} />
      <Meta label="Sources" value={currentPage.sources.length.toString()} />

      <div className="infobox-section">
        <h3>Tags</h3>
        <div className="tag-row" aria-label="Tags">
          {currentPage.tags.map((tag) => (
            <button
              className="tag"
              type="button"
              key={tag}
              onClick={() => setQuery(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      <div className="infobox-section">
        <h3>Source IDs</h3>
        <SourceList sources={currentPage.sources} />
      </div>
    </section>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="meta-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function AskCogneePanel({ currentPage }: { currentPage: WikiPage }) {
  const [question, setQuestion] = useState(`What should I understand about ${currentPage.title}?`);
  const [answer, setAnswer] = useState("");
  const [filedPath, setFiledPath] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setQuestion(`What should I understand about ${currentPage.title}?`);
    setAnswer("");
    setFiledPath("");
    setStatus("");
    setError("");
  }, [currentPage.path, currentPage.title]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;

    setLoading(true);
    setAnswer("");
    setFiledPath("");
    setStatus("");
    setError("");

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          question: trimmed,
          session: "karpathy-wiki-web",
          cognee: true,
          fileAnswer: true,
          reviewed: true,
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "query failed");
      setAnswer(payload.answer || "");
      setFiledPath(payload.filedPath || "");
      setStatus(payload.cogneeStatus || "");
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="tab-panel ask-panel">
      <h2>Ask Cognee</h2>
      <p className="panel-note">
        This calls the local wiki API, recalls Cognee memory, searches markdown evidence, and files the answer as a reviewed query synthesis page.
      </p>
      <form className="ask-form" onSubmit={submit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={3}
          aria-label="Question for Cognee"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Asking..." : "Ask and file reviewed answer"}
        </button>
      </form>
      {error ? (
        <p className="api-error">
          {error}. Start the API with <code>python3 scripts/wiki_server.py</code> or run the production server after <code>npm run build</code>.
        </p>
      ) : null}
      {status ? <p className="panel-note">Cognee status: <code>{status}</code></p> : null}
      {filedPath ? <p className="panel-note">Filed reviewed page: <code>{filedPath}</code></p> : null}
      {answer ? (
        <article className="api-answer">
          <MarkdownText markdown={answer} />
        </article>
      ) : null}
    </section>
  );
}

function GraphPanel({ currentPage }: { currentPage: WikiPage }) {
  const graph = cogneeGraphForPage(currentPage, 64);

  return (
    <section className="tab-panel">
      <h2>Cognee graph</h2>
      <p className="panel-note">
        Exported from Cognee dataset <code>{cogneeGraph.dataset}</code>: {cogneeGraph.nodeCount} nodes and {cogneeGraph.edgeCount} edges.
        This view shows a readable Cognee neighborhood for the current wiki page, with source records, entities, types, and relationship labels separated visually.
      </p>
      <CogneeGraphView currentPage={currentPage} graph={graph} large />
      {graph.nodes.length ? (
        <>
          <h3>Visible Cognee Relationships</h3>
          <table className="graph-relations">
            <thead>
              <tr>
                <th scope="col">From</th>
                <th scope="col">Relation</th>
                <th scope="col">To</th>
              </tr>
            </thead>
            <tbody>
              {graph.relationRows.map((row) => (
                <tr key={row.id}>
                  <td>{nodeLabelWithLink(row.source)}</td>
                  <td><code>{row.label}</code></td>
                  <td>{nodeLabelWithLink(row.target)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <p className="muted">{cogneeGraph.error ?? "No Cognee graph export is available yet."}</p>
      )}
    </section>
  );
}

function SourcesPanel({ currentPage }: { currentPage: WikiPage }) {
  const sourceNotes = pages.filter(
    (page) =>
      page.type === "source-note" &&
      page.sources.some((source) => currentPage.sources.includes(source))
  );

  return (
    <section className="tab-panel">
      <h2>Sources</h2>
      <p className="panel-note">
        Source IDs are the citation handles used by the markdown wiki and Cognee memory records.
      </p>
      <h3>Source IDs</h3>
      <SourceList sources={currentPage.sources} />

      <h3>Matching Source Notes</h3>
      {sourceNotes.length === 0 ? (
        <p className="muted">No matching source-note page was found for this page.</p>
      ) : (
        <ul className="link-list">
          {sourceNotes.map((page) => (
            <li key={page.path}>
              <a href={`#/${page.path}`}>{page.title}</a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function SourceList({ sources }: { sources: string[] }) {
  if (sources.length === 0) {
    return <p className="muted source-empty">No sources listed.</p>;
  }

  return (
    <ul className="source-list">
      {sources.map((source) => {
        const sourceNote = pages.find(
          (page) => page.type === "source-note" && page.sources.includes(source)
        );
        return (
          <li key={source}>
            {sourceNote ? (
              <a href={`#/${sourceNote.path}`}><code>{source}</code></a>
            ) : (
              <code>{source}</code>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function RelatedPanel({
  currentPage,
  backlinks
}: {
  currentPage: WikiPage;
  backlinks: WikiPage[];
}) {
  return (
    <section className="tab-panel">
      <h2>Related pages</h2>
      <div className="relations related-tab">
        <RelatedList title="Related" currentPath={currentPage.path} links={currentPage.related} />
        <BacklinksList backlinks={backlinks} />
      </div>
    </section>
  );
}

function KnowledgeGraph({ currentPage, large = false }: { currentPage: WikiPage; large?: boolean }) {
  if (cogneeGraph.nodes.length) {
    return <CogneeGraphView currentPage={currentPage} large={large} />;
  }
  return <WikiGraphView currentPage={currentPage} large={large} />;
}

function CogneeGraphView({
  currentPage,
  large = false,
  graph: providedGraph
}: {
  currentPage: WikiPage;
  large?: boolean;
  graph?: CogneeGraphResult;
}) {
  const graph = providedGraph ?? cogneeGraphForPage(currentPage, large ? 64 : 28);
  const viewBox = large ? "0 0 760 500" : "0 0 560 340";
  const markerId = large ? "cognee-arrow-large" : "cognee-arrow-small";

  return (
    <section className={`graph-box cognee ${large ? "large" : ""}`}>
      <h2>Cognee graph</h2>
      <div className="graph-stats">
        <span>{cogneeGraph.nodeCount} nodes</span>
        <span>{cogneeGraph.edgeCount} edges</span>
        <span>{graph.nodes.length} shown</span>
        <span>{graph.anchorCount} anchors</span>
        <span>{graph.hiddenCount} hidden</span>
      </div>
      <svg className="knowledge-graph" viewBox={viewBox} role="img" aria-label={`Cognee graph around ${currentPage.title}`}>
        <defs>
          <marker id={markerId} markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
            <path d="M0,0 L0,6 L7,3 z" />
          </marker>
        </defs>
        {graph.edges.map((edge, index) => (
          <line
            key={`${edge.source}-${edge.target}-${edge.label}-${index}`}
            className={`cognee-edge ${relationshipClass(edge.label)}`}
            x1={edge.sourceNode.x}
            y1={edge.sourceNode.y}
            x2={edge.targetNode.x}
            y2={edge.targetNode.y}
            markerEnd={`url(#${markerId})`}
          />
        ))}
        {large
          ? graph.edges
              .filter((edge) => edge.label !== "contains")
              .slice(0, 24)
              .map((edge, index) => (
                <text
                  key={`${edge.source}-${edge.target}-${edge.label}-label-${index}`}
                  className="cognee-edge-label"
                  x={(edge.sourceNode.x + edge.targetNode.x) / 2}
                  y={(edge.sourceNode.y + edge.targetNode.y) / 2 - 4}
                >
                  {edge.displayLabel}
                </text>
              ))
          : null}
        {graph.nodes.map((node) => {
          const content = (
            <g className={`cognee-node ${node.active ? "active" : ""} group-${node.group} type-${node.type}`}>
              <circle cx={node.x} cy={node.y} r={node.active ? (large ? 25 : 18) : (large ? 14 : 10)} />
              <text className="node-label" x={node.x} y={node.y + (node.active ? 39 : 27)}>
                {truncateLabel(node.displayLabel, large ? 30 : 18)}
              </text>
              {large ? (
                <text className="node-detail" x={node.x} y={node.y + (node.active ? 54 : 41)}>
                  {truncateLabel(node.detail, 24)}
                </text>
              ) : null}
              <title>{node.description || `${node.type}: ${node.displayLabel}`}</title>
            </g>
          );

          return node.wikiPath ? (
            <a href={`#/${node.wikiPath}`} key={node.id} className="graph-link">
              {content}
            </a>
          ) : (
            <g key={node.id}>{content}</g>
          );
        })}
      </svg>
      <div className="graph-legend" aria-label="Cognee graph legend">
        <span><i className="legend-anchor" /> Page/source anchor</span>
        <span><i className="legend-source-node" /> Source memory</span>
        <span><i className="legend-entity" /> Entity</span>
        <span><i className="legend-type" /> EntityType</span>
        <span><i className="legend-is-a" /> is_a</span>
      </div>
    </section>
  );
}

function nodeLabelWithLink(node: CogneeVisualNode): React.ReactNode {
  const label = (
    <>
      {node.displayLabel}
      <span className="muted"> ({node.type})</span>
    </>
  );
  return node.wikiPath ? <a href={`#/${node.wikiPath}`}>{label}</a> : label;
}

function WikiGraphView({ currentPage, large = false }: { currentPage: WikiPage; large?: boolean }) {
  const graph = graphForPage(currentPage);

  return (
    <section className={`graph-box wiki-fallback ${large ? "large" : ""}`}>
      <h2>Wiki link graph fallback</h2>
      <svg className="knowledge-graph" viewBox="0 0 560 340" role="img" aria-label={`Graph around ${currentPage.title}`}>
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
            <path d="M0,0 L0,6 L7,3 z" />
          </marker>
        </defs>
        {graph.edges.map((edge) => {
          const from = graph.nodes.find((node) => node.id === edge.from);
          const to = graph.nodes.find((node) => node.id === edge.to);
          if (!from || !to) return null;
          return (
            <line
              key={`${edge.from}-${edge.to}-${edge.kind}`}
              className={`graph-edge ${edge.kind}`}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
            />
          );
        })}
        {graph.nodes.map((node) => (
          <a href={`#/${node.page.path}`} key={node.id} className="graph-link">
            <g className={`graph-node ${node.active ? "active" : ""} ${node.page.type}`}>
              <circle cx={node.x} cy={node.y} r={node.active ? 32 : 23} />
              <text x={node.x} y={node.y + (node.active ? 45 : 36)}>{truncateLabel(node.page.title)}</text>
            </g>
          </a>
        ))}
      </svg>
      <div className="graph-legend" aria-label="Graph legend">
        <span><i className="legend-link" /> link</span>
        <span><i className="legend-source" /> source</span>
        <span><i className="legend-tag" /> tag</span>
      </div>
    </section>
  );
}

function relationshipClass(label: string): string {
  if (label === "is_a") return "is-a";
  if (label.includes("related")) return "related";
  if (label.includes("contains")) return "contains";
  if (label.includes("part_of") || label.includes("made_from")) return "composition";
  return "semantic";
}

function formatRelationship(label: string): string {
  return label.replace(/_/g, " ");
}

function truncateLabel(value: string, limit = 24): string {
  return value.length > limit ? `${value.slice(0, limit - 3)}...` : value;
}

function RelatedList({
  title,
  currentPath,
  links
}: {
  title: string;
  currentPath: string;
  links: string[];
}) {
  return (
    <div>
      <h2>{title}</h2>
      {links.length === 0 ? (
        <p className="muted">No related pages yet.</p>
      ) : (
        <ul className="link-list">
          {links.map((href) => {
            const resolved = resolvePath(currentPath, href);
            const page = pageByPath.get(resolved);
            return (
              <li key={href}>
                {page ? (
                  <a href={`#/${resolved}`}>{page.title}</a>
                ) : (
                  <span className="missing-link">{href}</span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function BacklinksList({ backlinks }: { backlinks: WikiPage[] }) {
  return (
    <div>
      <h2>Backlinks</h2>
      {backlinks.length === 0 ? (
        <p className="muted">No backlinks yet.</p>
      ) : (
        <ul className="link-list">
          {backlinks.map((page) => (
            <li key={page.path}>
              <a href={`#/${page.path}`}>{page.title}</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function MarkdownText({ markdown }: { markdown: string }) {
  const page: WikiPage = {
    path: "index.md",
    title: "API Answer",
    type: "source-note",
    status: "reviewed",
    tags: [],
    aliases: [],
    related: [],
    sources: [],
    confidence: "medium",
    body: markdown,
    raw: markdown,
  };
  return <Markdown page={page} />;
}

function Markdown({ page }: { page: WikiPage }) {
  const lines = page.body.split(/\r?\n/);
  const blocks: React.ReactNode[] = [];
  let listItems: string[] = [];
  let codeLines: string[] = [];
  let inCode = false;

  const flushList = () => {
    if (listItems.length === 0) return;
    blocks.push(
      <ul key={`list-${blocks.length}`}>
        {listItems.map((item, index) => (
          <li key={index}>{renderInline(item, page)}</li>
        ))}
      </ul>
    );
    listItems = [];
  };

  const flushCode = () => {
    blocks.push(
      <pre key={`code-${blocks.length}`}>
        <code>{codeLines.join("\n")}</code>
      </pre>
    );
    codeLines = [];
  };

  for (const line of lines) {
    if (line.startsWith("```")) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        flushList();
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (!line.trim()) {
      flushList();
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      flushList();
      const level = heading[1].length;
      const text = heading[2];
      const id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      if (level === 1) blocks.push(<h1 id={id} key={blocks.length}>{text}</h1>);
      if (level === 2) blocks.push(<h2 id={id} key={blocks.length}>{text}</h2>);
      if (level === 3) blocks.push(<h3 id={id} key={blocks.length}>{text}</h3>);
      if (level >= 4) blocks.push(<h4 id={id} key={blocks.length}>{text}</h4>);
      continue;
    }

    const list = line.match(/^-\s+(.*)$/);
    if (list) {
      listItems.push(list[1]);
      continue;
    }

    flushList();
    blocks.push(
      <p key={`p-${blocks.length}`}>{renderInline(line, page)}</p>
    );
  }

  flushList();
  if (inCode) flushCode();

  return <>{blocks}</>;
}

function renderInline(text: string, page: WikiPage): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  const regex = /`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)|\*\*([^*]+)\*\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) nodes.push(text.slice(lastIndex, match.index));

    if (match[1]) {
      nodes.push(<code key={match.index}>{match[1]}</code>);
    } else if (match[2] && match[3]) {
      const href = match[3];
      const resolved = resolvePath(page.path, href);
      const upstream = resolveUpstreamSourceLink(page, href);
      if (/^https?:/.test(href)) {
        nodes.push(
          <a key={match.index} href={href} target="_blank" rel="noreferrer">
            {match[2]}
          </a>
        );
      } else if (pageByPath.has(resolved)) {
        nodes.push(
          <a key={match.index} href={`#/${resolved}`}>
            {match[2]}
          </a>
        );
      } else if (upstream) {
        nodes.push(
          <a key={match.index} href={upstream} target="_blank" rel="noreferrer">
            {match[2]}
          </a>
        );
      } else {
        nodes.push(
          <span key={match.index} className="missing-link">
            {match[2]}
          </span>
        );
      }
    } else if (match[4]) {
      nodes.push(<strong key={match.index}>{match[4]}</strong>);
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) nodes.push(text.slice(lastIndex));
  return nodes;
}

function resolveUpstreamSourceLink(page: WikiPage, href: string): string | null {
  if (page.type !== "source-note") return null;
  if (/^(https?:|mailto:|#)/.test(href)) return null;
  const base = upstreamSourceBase(page);
  if (!base) return null;

  try {
    return new URL(href, base).toString();
  } catch {
    return null;
  }
}

function upstreamSourceBase(page: WikiPage): string | null {
  const match = page.body.match(/^- URL(?: or local record)?:\s*(https?:\/\/\S+)/m);
  return match?.[1] ?? null;
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
