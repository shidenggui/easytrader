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
public class fiximage {

	public static void main(String[] args) throws Exception {
		boolean isDebug = true;
		BufferedImage img = removeBackgroud("/Users/darkness/git/easytrader/temp/0.jpg");
		if (isDebug) {
			ImageIO.write(img, "JPG", new File("/Users/darkness/git/easytrader/abc/" + "aaa.jpg"));
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
//		minThreshold *= 3;
		for (int y = 0; y < h; y++) {
			for (int x = 0; x < w; x++) {
				final Color color = new Color(img.getRGB(x, y));
				int rgb = color.getRed();
				if (rgb > 240 && color.getGreen() < 20) {// && rgb < maxThreshold) {
					newImg.setRGB(x, y, min.getRGB());
				} else {
					newImg.setRGB(x, y, max.getRGB());
				} 
			}
		}
		return newImg;
	}
}
