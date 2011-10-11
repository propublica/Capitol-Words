code = "{{ code }}"
iframe = "<iframe src='http://capitolwords.org/embed/#{code}?embedder=#{encodeURIComponent(window.location.href)}&embedder_host=#{encodeURIComponent(window.location.host)}' width='575' height='400' frameborder='0' scrolling='no'></iframe>"
document.write(iframe)
