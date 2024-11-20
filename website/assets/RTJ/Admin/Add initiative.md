<%*
// get current file title 
const current = tp.file.find_tfile(tp.file.title);
// choose between initiative files
let file = await tp.system.suggester(f => f.basename, app.vault.getMarkdownFiles().filter(file => file.path.includes('Initiatives/')),true,"Choose an initiative for this file")
let initiative = "[["+file.basename+"]]"
// Update initiative property
await app.fileManager.processFrontMatter(current, (frontmatter) => {
	frontmatter["initiative"] = initiative;
});
_%>