# noticed
"Noticed" is backend failure notification daemon for NGINX using Telegram.  

**Installation:**  
Just download latest version and modify config.
  
**Usage:** 
```
./noticed.py
```
  
**Requirements**
* Python 3.4 or greater  
* URLLib3  
* Certifi  
  
**Configuration**
Copy noticed.conf into your nginx directory and add 'include noticed.conf' into your server{} block.  
  
**noticed.conf**  
```
error_page 502 503 504 /noticed.html;

location /noticed.html {
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header Host $http_host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Request-URI $request_uri;

  proxy_pass http://127.0.0.1:8081/;
  error_page 502 503 504 /var/www/html/errors/servertechworks.html;
}

```

