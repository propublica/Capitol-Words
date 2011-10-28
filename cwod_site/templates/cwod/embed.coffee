code = "{{ code }}"
iframe = "<iframe src='http://capitolwords.org/embed/#{code}?embedder=#{encodeURIComponent(window.location.href)}&embedder_host=#{encodeURIComponent(window.location.host)}' width='630' height='325' frameborder='0' scrolling='no'></iframe>"
document.write(iframe)
