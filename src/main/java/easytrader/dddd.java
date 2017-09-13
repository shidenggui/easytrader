package easytrader;

import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

import org.apache.commons.io.IOUtils;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClientBuilder;

public class dddd {

	public static void main(String[] args) {
		downloadImage("https://trade.gf.com.cn/yzm.jpgx");
	}
	 public static void downloadImage(String url) {  
	        HttpClient httpClient = HttpClientBuilder.create().build();
	        
	        HttpGet httpGet2 = null;  
	        for (int i = 0; i < 1; i++) {  
	        	httpGet2 = new HttpGet(url + "?random=0.2" + (2000 + i));
				
				httpGet2.addHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8");
				httpGet2.addHeader("Accept-Encoding", "gzip, deflate, sdch");
				httpGet2.addHeader("Accept-Language", "zh-CN,zh;q=0.8");
				httpGet2.addHeader("Cache-Control", "max-age=0");
				httpGet2.addHeader("Connection", "keep-alive");
				httpGet2.addHeader("Host", "trade.gf.com.cn");
				httpGet2.addHeader("Cookie", "name=value; JSESSIONID=7F61DE7C93B9A50336C9E481E15D427F");
//				httpGet2.addHeader("Referer", "https://service.htsc.com.cn/service/loginAction.do?method=tologin&sub_top=sy");
				httpGet2.addHeader("User-Agent",
						"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36");

				
	            try {  
	                // 执行getMethod  
	            	HttpResponse response = httpClient.execute(httpGet2);  
//	                if (response. != HttpStatus.SC_OK) {  
//	                    System.err.println("Method failed: "  
//	                            + getMethod.getStatusLine());  
//	                }  
	                // 读取内容  
	                String picName = "temp//" + i + ".jpg";  
	                InputStream inputStream = response.getEntity().getContent();  
	                OutputStream outStream = new FileOutputStream(picName);  
	                IOUtils.copy(inputStream, outStream);  
	                outStream.close();  
	                System.out.println(i + "OK!");  
	            } catch (Exception e) {  
	                e.printStackTrace();  
	            } finally {  
	                // 释放连接  
	            	httpGet2.releaseConnection();  
	            }  
	        }  
	    }  
}
