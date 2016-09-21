package easytrader;

import java.io.File;

import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;

/**
 *  
 * @author Darkness
 * @date 2016年9月21日 下午5:57:10
 * @version V1.0
 */
public class xxx {

	public static void main(String[] args) {
		File imageFile = new File("/Users/darkness/git/easytrader/temp/0.jpg");  
	       Tesseract tessreact = new Tesseract();  
//	       tessreact.setDatapath("C:\\Users\\Administrator\\git\\easytrader\\tessdata-master");  
	       try {  
	           String result = tessreact.doOCR(imageFile);  
	           System.out.println(result);  
	       } catch (TesseractException e) {  
	           System.err.println(e.getMessage());  
	       }
	}
}
