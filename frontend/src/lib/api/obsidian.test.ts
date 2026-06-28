import { describe, expect, it } from "vitest";

import {
  extractVaultNameFromFiles,
  filterMarkdownFiles,
} from "@/lib/api/obsidian";

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

  it("sends relative_paths_json separately from file uploads", () => {
    const file = new File(["# Note"], "note.md", { type: "text/markdown" });
    Object.defineProperty(file, "webkitRelativePath", {
      value: "Research/notes/note.md",
    });
    const formData = new FormData();
    formData.append(
      "relative_paths_json",
      JSON.stringify([file.webkitRelativePath || file.name]),
    );
    formData.append("files", file, file.name);
    expect(formData.get("relative_paths_json")).toBe(
      JSON.stringify(["Research/notes/note.md"]),
    );
    expect((formData.get("files") as File).name).toBe("note.md");
  });
});
