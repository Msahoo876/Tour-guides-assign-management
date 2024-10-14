function showContent(content) {
    fetch(`/content/${content}`)
    .then(response => response.text())
    .then(data => {
        document.getElementById('main-content').innerHTML = data;
    });
}
