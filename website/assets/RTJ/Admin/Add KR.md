<%*
// Get the current file tfile 
const current = tp.file.find_tfile(tp.file.path(true));

// Extract the keyword from the path if it contains any of the terms "good traits", "bad traits", or "worship"
let path = tp.file.path(false);
let KR = '';
if (path.includes('good traits')) {
    KR = 'good traits';
} else if (path.includes('bad traits')) {
    KR = 'bad traits';
} else if (path.includes('worship')) {
    KR = 'worship';
} else {
    KR = null
}
new Notice(KR)
// Update the frontmatter with the KR value
await app.fileManager.processFrontMatter(current, (frontmatter) => {
    frontmatter["KR"] = KR;
});
_%>