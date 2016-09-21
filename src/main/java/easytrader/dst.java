package easytrader;

import java.io.File;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;

import org.bytedeco.javacpp.BytePointer;
import org.bytedeco.javacpp.lept;
import org.bytedeco.javacpp.lept.PIX;
import org.bytedeco.javacpp.tesseract.TessBaseAPI;

/**
 *  
 * @author Darkness
 * @date 2016年9月21日 下午5:03:25
 * @version V1.0
 */
public class dst {

	//http://blog.sina.com.cn/s/blog_68b0f46d0102wb57.html
	public static void main(String[] args) {
		File abc = new File("/Users/darkness/git/easytrader/abc");
		List<String> errors = new ArrayList<>();
		for (File string : abc.listFiles()) {
			String code = process(string.getPath());
			if(code.length() !=5) {
				errors.add("识别失败：" + code + "==" + string.getName());
			} else {
				System.out.println(code + "==" + string.getName());
			}
		}
		
		for (String string : errors) {
			System.out.println(string);
		}
		
	}
	
	public static String process(String file) {
        TessBaseAPI api = new TessBaseAPI();
        
        if (api.Init(".", "eng") != 0) {
            throw new RuntimeException("Could not initialize tesseract.");
        }       
        api.SetVariable("tessedit_char_whitelist", "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ");
        
        PIX image = null;
        BytePointer outText = null;
        try {
            image = lept.pixRead(file);
            api.SetImage(image);
            outText = api.GetUTF8Text();
            String string = outText.getString("UTF-8");
            if (string != null) {
            	
                string = trim(string);
            }
            return string;
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException("charset", e);
        } finally {
            if (outText != null) {
                outText.deallocate();
            }
            if (image != null) {
                lept.pixDestroy(image);
            }
            if (api != null) {
                api.End();
            }
        }
    }
	
	private static String trim(String string) {
		return string.replaceAll(" ", "").replaceAll("\n", "");
	}
}
