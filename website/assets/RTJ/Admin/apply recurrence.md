<%*
// convert todays date based on recurrence property
const nlInput = tp.frontmatter.recurrence
const date = nlInput ? app.plugins.plugins["nldates-obsidian"].parseDate(nlInput).moment.format('YYYY-MM-DD') : '';
// change date property
const file = tp.file.find_tfile(tp.file.path(true));
await app.fileManager.processFrontMatter(file, (frontmatter) => {
  // Replace "updated" with the key you use
  frontmatter["due"] = date;
});
-%>