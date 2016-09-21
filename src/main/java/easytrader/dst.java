package easytrader;

import java.io.UnsupportedEncodingException;

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

	public static void main(String[] args) {
		String code = process("C:\\Users\\Administrator\\git\\easytrader\\temp\\0.jpg");
		System.out.println(code);
	}
	
	public static String process(String file) {
        TessBaseAPI api = new TessBaseAPI();
        
        if (api.Init(".", "pol") != 0) {
            throw new RuntimeException("Could not initialize tesseract.");
        }       
        PIX image = null;
        BytePointer outText = null;
        try {
            image = lept.pixRead(file);
            api.SetImage(image);
            outText = api.GetUTF8Text();
            String string = outText.getString("UTF-8");
            if (string != null) {
                string = string.trim();
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
}
