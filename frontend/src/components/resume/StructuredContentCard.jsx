function sanitizeInline(text) {
  return String(text || "")
    .replace(/\*\*/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function parseStructuredContent(text) {
  const lines = String(text || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  const blocks = [];
  let listBuffer = null;

  const flushList = () => {
    if (listBuffer?.items?.length) {
      blocks.push(listBuffer);
    }
    listBuffer = null;
  };

  lines.forEach((line) => {
    const cleaned = sanitizeInline(line);
    if (!cleaned) {
      flushList();
      return;
    }

    const orderedMatch = cleaned.match(/^(\d+)[.)]\s+(.*)$/);
    if (orderedMatch) {
      if (!listBuffer || listBuffer.type !== "ordered") {
        flushList();
        listBuffer = { type: "ordered", items: [] };
      }
      listBuffer.items.push(orderedMatch[2]);
      return;
    }

    const bulletMatch = cleaned.match(/^[-*•]\s+(.*)$/);
    if (bulletMatch) {
      if (!listBuffer || listBuffer.type !== "unordered") {
        flushList();
        listBuffer = { type: "unordered", items: [] };
      }
      listBuffer.items.push(bulletMatch[1]);
      return;
    }

    flushList();

    if (cleaned.endsWith(":")) {
      blocks.push({ type: "heading", content: cleaned.slice(0, -1) });
      return;
    }

    const splitHeading = cleaned.match(/^([^:]{2,60}):\s+(.*)$/);
    if (splitHeading && splitHeading[1].split(" ").length <= 6) {
      blocks.push({
        type: "callout",
        heading: splitHeading[1],
        content: splitHeading[2]
      });
      return;
    }

    blocks.push({ type: "paragraph", content: cleaned });
  });

  flushList();
  return blocks;
}

function StructuredContentCard({ title, text, source, accent = "slate" }) {
  const accentMap = {
    slate: "bg-slate-50 text-slate-700 border-slate-200",
    brand: "bg-brand-50 text-brand-900 border-brand-100",
    emerald: "bg-emerald-50 text-emerald-900 border-emerald-100"
  };

  const blocks = parseStructuredContent(text);
  const calloutClass = accentMap[accent] || accentMap.slate;

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>

      <div className="mt-4 space-y-3">
        {blocks.length ? (
          blocks.map((block, index) => {
            if (block.type === "heading") {
              return (
                <div key={`${block.content}-${index}`} className="pt-1">
                  <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">{block.content}</p>
                </div>
              );
            }

            if (block.type === "callout") {
              return (
                <div key={`${block.heading}-${index}`} className={`rounded-xl border p-4 ${calloutClass}`}>
                  <p className="text-sm font-semibold">{block.heading}</p>
                  <p className="mt-1 text-sm leading-6">{block.content}</p>
                </div>
              );
            }

            if (block.type === "ordered" || block.type === "unordered") {
              const ListTag = block.type === "ordered" ? "ol" : "ul";
              return (
                <ListTag
                  key={`list-${index}`}
                  className={`space-y-2 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700 ${
                    block.type === "ordered" ? "list-decimal pl-8" : "list-disc pl-8"
                  }`}
                >
                  {block.items.map((item, itemIndex) => (
                    <li key={`${item}-${itemIndex}`} className="pr-2 leading-6">
                      {item}
                    </li>
                  ))}
                </ListTag>
              );
            }

            return (
              <p key={`${block.content}-${index}`} className="rounded-xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-700">
                {block.content}
              </p>
            );
          })
        ) : (
          <div className="rounded-lg border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500">
            No content returned.
          </div>
        )}
      </div>

      {source ? <p className="mt-4 text-xs text-slate-500">Source: {source}</p> : null}
    </article>
  );
}

export default StructuredContentCard;
