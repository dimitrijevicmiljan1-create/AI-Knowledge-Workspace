import { describe, expect, it } from "vitest";

import {
  extractVaultNameFromFiles,
  filterMarkdownFiles,
} from "@/lib/api/obsidian";

function getUploadRelativePath(file: File): string {
  return file.webkitRelativePath || file.name;
}

describe("obsidian api helpers", () => {
  it("filters markdown files only", () => {
    const files = [
      new File(["# Note"], "note.md", { type: "text/markdown" }),
      new File(["png"], "image.png", { type: "image/png" }),
    ];
    expect(filterMarkdownFiles(files)).toHaveLength(1);
  });

  it("extracts the vault name from webkitRelativePath", () => {
    const file = new File(["# Note"], "note.md", { type: "text/markdown" });
    Object.defineProperty(file, "webkitRelativePath", {
      value: "Research/notes/note.md",
    });
    expect(extractVaultNameFromFiles([file])).toBe("Research");
  });

  it("prefers webkitRelativePath for upload filenames", () => {
    const file = new File(["# Note"], "note.md", { type: "text/markdown" });
    Object.defineProperty(file, "webkitRelativePath", {
      value: "Research/notes/note.md",
    });
    expect(getUploadRelativePath(file)).toBe("Research/notes/note.md");
  });
});
