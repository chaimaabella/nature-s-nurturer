const escapeHtml = (value: string) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

const formatInlineMarkdown = (value: string) =>
  value
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em class="italic">$1</em>');

export const markdownToHtml = (markdown: string) => {
  if (!markdown) return "";
  const escaped = escapeHtml(markdown);
  const lines = escaped.split("\n");
  const blocks: string[] = [];
  let paragraphLines: string[] = [];
  let listItems: string[] = [];
  let listType: "ol" | "ul" | null = null;

  const flushParagraph = () => {
    if (!paragraphLines.length) return;
    const content = formatInlineMarkdown(paragraphLines.join(" "));
    blocks.push(`<p class="mb-2 last:mb-0">${content}</p>`);
    paragraphLines = [];
  };

  const flushList = () => {
    if (!listType || !listItems.length) return;
    const className =
      listType === "ol"
        ? 'class="ml-4 list-decimal space-y-1"'
        : 'class="ml-4 list-disc space-y-1"';
    blocks.push(`<${listType} ${className}>${listItems.join("")}</${listType}>`);
    listItems = [];
    listType = null;
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      flushList();
      continue;
    }

    const orderedMatch = trimmed.match(/^\d+\.\s+(.*)$/);
    const unorderedMatch = trimmed.match(/^[-*]\s+(.*)$/);

    if (orderedMatch) {
      flushParagraph();
      if (listType && listType !== "ol") {
        flushList();
      }
      listType = "ol";
      listItems.push(`<li>${formatInlineMarkdown(orderedMatch[1])}</li>`);
      continue;
    }

    if (unorderedMatch) {
      flushParagraph();
      if (listType && listType !== "ul") {
        flushList();
      }
      listType = "ul";
      listItems.push(`<li>${formatInlineMarkdown(unorderedMatch[1])}</li>`);
      continue;
    }

    if (listType) {
      flushList();
    }
    paragraphLines.push(trimmed);
  }

  flushParagraph();
  flushList();

  return blocks.join("");
};
