<%*
// get current file tfile 
const current = tp.file.find_tfile(tp.file.path(true));
// choose between initiative files
let file = await tp.system.suggester(f => f.basename, app.vault.getMarkdownFiles().filter(file => file.path.includes('Objective/')),true,"Choose a domain for this file")
let domain = "[["+file.basename+"]]"
// Update initiative property
await app.fileManager.processFrontMatter(current, (frontmatter) => {
	frontmatter["domain"] = domain;
});
_%>