package easytrader;

import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;

import javax.imageio.ImageIO;

import ocr.gf.ImageUtil;

/**
 * 
 * @author Darkness
 * @date 2016年9月21日 下午6:08:39
 * @version V1.0
 */
public class fiximage2 {

	public static void main(String[] args) throws Exception {
		boolean isDebug = true;
		
		
		File temp = new File("/Users/darkness/git/easytrader/temp");
		for(File imageFile : temp.listFiles())  {
			BufferedImage img = removeBackgroud(imageFile.getPath());
			if (isDebug) {
				ImageIO.write(img, "JPG", new File(imageFile.getPath().replace("temp", "abc")));
			}	
		}
	}

	public static BufferedImage removeBackgroud(String picFile) throws Exception {
		BufferedImage img = ImageIO.read(new File(picFile));
		img = filterThreshold(img, 200, 300);// removeBackgroud(string);
		return img;
	}
	
	public static BufferedImage filterThreshold(BufferedImage img, int minThreshold, int maxThreshold) {
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
}
