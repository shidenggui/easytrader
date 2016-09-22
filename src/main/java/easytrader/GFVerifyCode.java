package easytrader;

import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;

import javax.imageio.ImageIO;

import org.bytedeco.javacpp.BytePointer;
import org.bytedeco.javacpp.lept;
import org.bytedeco.javacpp.lept.PIX;
import org.bytedeco.javacpp.tesseract.TessBaseAPI;

/**
 * 
 * @author Darkness
 * @date 2016年9月21日 下午6:08:39
 * @version V1.0
 */
public class GFVerifyCode {

//	public static void main(String[] args) throws Exception {
//		boolean isDebug = true;
//		
//		
//		File temp = new File("/Users/darkness/git/easytrader/temp");
//		for(File imageFile : temp.listFiles())  {
//			BufferedImage image = ImageIO.read(new File(imageFile.getPath()));
//			BufferedImage img = removeBackgroud(image);
//			if (isDebug) {
//				ImageIO.write(img, "JPG", new File(imageFile.getPath().replace("temp", "abc")));
//			}	
//		}
//	}
	
	private static String userDir() {
		return System.getProperty("user.dir") + File.separator;
	}
	
	//http://blog.sina.com.cn/s/blog_68b0f46d0102wb57.html
	public static void main(String[] args) throws IOException {
		File abc = new File(userDir() + "temp");
		List<String> errors = new ArrayList<>();
		for (File string : abc.listFiles()) {
			if(!string.getName().endsWith(".jpg")) {
				continue;
			}
			BufferedImage image = ImageIO.read(new File(string.getPath()));
			GFVerifyCode verifyCode = new GFVerifyCode(image);
			String code = verifyCode.getValue();
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
	
	private BufferedImage image;
	private String value;
	
	public GFVerifyCode(BufferedImage image) {
		this.image = image;
	}
	
	public String getValue() {
		try {
			this.image = removeBackgroud(this.image);
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		String code = process(this.image);
		this.value = code;
		return code;
	}

	private static BufferedImage removeBackgroud(BufferedImage img) throws Exception {
//		BufferedImage img = ImageIO.read(new File(picFile));
		img = filterThreshold(img, 200, 300);// removeBackgroud(string);
		return img;
	}
	
	private static BufferedImage filterThreshold(BufferedImage img, int minThreshold, int maxThreshold) {
		final int w = img.getWidth();
		final int h = img.getHeight();
		final BufferedImage newImg = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
		Color min = Color.BLACK;
		Color max = Color.WHITE;
		if (minThreshold < 0) {
			min = Color.WHITE;
			max = Color.BLACK;
			minThreshold = -minThreshold;
		}
//		Color mycolor = new Color(256, 256, 256);
//		minThreshold *= 3;
		for (int y = 0; y < h; y++) {
			for (int x = 0; x < w; x++) {
				final Color color = new Color(img.getRGB(x, y));
//				System.out.println("" + color.getRed() + "=="+ color.getGreen() + "=="+ color.getBlue() + "==");
				if(color.getRed()>200 && color.getGreen() <50 && color.getBlue() <50) {
//					if(color.getRed()<100 && color.getGreen() < 100 && color.getBlue() <100) {
					newImg.setRGB(x, y, min.getRGB());
				} else {
					newImg.setRGB(x, y, max.getRGB());
				}
			}
		}
		return newImg;
	}
	
	public static String process(BufferedImage bufferedImage) {
        TessBaseAPI api = new TessBaseAPI();
        
        
        if (api.Init(".", "eng") != 0) {
            throw new RuntimeException("Could not initialize tesseract.");
        }       
        api.SetVariable("tessedit_char_whitelist", "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ");
        
        PIX image = null;
        BytePointer outText = null;
        try {
        	ByteArrayOutputStream out = new ByteArrayOutputStream();  
            boolean flag = ImageIO.write(bufferedImage, "png", out);  
            byte[] b = out.toByteArray();  

            image = lept.pixReadMem(b, b.length);
            api.SetImage(image);
            outText = api.GetUTF8Text();
            String string = outText.getString("UTF-8");
            if (string != null) {
            	
                string = trim(string);
            }
            return string;
        } catch (Exception e) {
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
