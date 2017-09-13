package ocr.gf;
import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.imageio.ImageIO;

import org.apache.commons.io.IOUtils;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClientBuilder;

/**   
 * 
 * @author Darkness
 * @date 2015-8-18 下午4:18:07 
 * @version V1.0   
 */
 class HtOcrReader {  
  
    private static Map<BufferedImage, String> trainMap = null;  
    private static int index = 0;  
  
    public static int isBlack(int colorInt) {  
        Color color = new Color(colorInt);  
        if (color.getRed() + color.getGreen() + color.getBlue() <= 100) {  
            return 1;  
        }  
        return 0;  
    }  
  
    public static int isWhite(int colorInt) {  
        Color color = new Color(colorInt);  
        if (color.getRed() + color.getGreen() + color.getBlue() > 100) {  
            return 1;  
        }  
        return 0;  
    }  
  
    public static BufferedImage removeBackgroud(String picFile)  
            throws Exception {  
        BufferedImage img = ImageIO.read(new File(picFile));  
        img = ImageUtil.filterThreshold(img, 200, 300);//removeBackgroud(string);
        return img;  
    }  
    
    public static BufferedImage removeBackgroud(BufferedImage img)  
            throws Exception {  
        img = ImageUtil.filterThreshold(img, 150);//removeBackgroud(string);
        return img;  
    }  
  
    public static BufferedImage removeBlank(BufferedImage img) throws Exception {  
        int width = img.getWidth();  
        int height = img.getHeight();  
        int start = 0;  
        int end = 0;  
        Label1: for (int y = 0; y < height; ++y) {  
            int count = 0;  
            for (int x = 0; x < width; ++x) {  
                if (isWhite(img.getRGB(x, y)) != 1) {  
                    count++;  
                }  
                if (count >= 1) {  
                    start = y;  
                    break Label1;  
                }  
            }  
        }  
        Label2: for (int y = height - 1; y >= 0; --y) {  
            int count = 0;  
            for (int x = 0; x < width; ++x) {  
                if (isWhite(img.getRGB(x, y)) != 1) {  
                    count++;  
                }  
                if (count >= 1) {  
                    end = y;  
                    break Label2;  
                }  
            }  
        }  
        return img.getSubimage(0, start, width, end - start + 1);  
    }  
  
    public static List<BufferedImage> splitImage(BufferedImage img)  
            throws Exception {  
        List<BufferedImage> subImgs = new ArrayList<BufferedImage>();  
        int width = img.getWidth();  
        int height = img.getHeight();  
        List<Integer> weightlist = new ArrayList<Integer>();  
        for (int x = 0; x < width; ++x) {  
            int count = 0;  
            for (int y = 0; y < height; ++y) {  
                if (isWhite(img.getRGB(x, y)) != 1) {  
                    count++;  
                }  
            }  
            weightlist.add(count);  
        }  
        
        int listLength = weightlist.size();
        for (int i = 0; i < listLength;) {  
            int length = 0;  
            while (i<listLength && weightlist.get(i++) > 1) {  
                length++;  
            }  
            if(length < 10) {
            	continue;
            }
            System.out.println(length);
            if (length > 50) {  
            	System.out.println(length);
                subImgs.add(removeBlank(img.getSubimage(i - length - 1, 0,  
                        length / 2, height)));  
                subImgs.add(removeBlank(img.getSubimage(i - length / 2 - 1, 0,  
                        length / 2, height)));  
            } else
            
            
           if (length > 3) {  
        	   int x = i - length - 1;
        	   int y = 0;
        	   int _width = length;
               subImgs.add(removeBlank(img.getSubimage(x, y,  
                		_width, height)));  
            }  
        }  
        return subImgs;  
    }  
  
    public static Map<BufferedImage, String> loadTrainData() throws Exception {  
        if (trainMap == null) {  
            Map<BufferedImage, String> map = new HashMap<BufferedImage, String>();  
            File dir = new File("train2");  
            File[] files = dir.listFiles();  
            for (File file : files) {  
                map.put(ImageIO.read(file), file.getName().charAt(0) + "");  
            }  
            trainMap = map;  
        }  
        return trainMap;  
    }  
  
    public static String getSingleCharOcr(BufferedImage img,  
            Map<BufferedImage, String> map) {  
        String result = "";  
        int width = img.getWidth();  
        int height = img.getHeight();  
        int min = width * height;  
        for (BufferedImage bi : map.keySet()) {  
            int count = 0;  
            int widthmin = width < bi.getWidth() ? width : bi.getWidth();  
            int heightmin = height < bi.getHeight() ? height : bi.getHeight();  
            Label1: for (int x = 0; x < widthmin; ++x) {  
                for (int y = 0; y < heightmin; ++y) {  
                    if (isWhite(img.getRGB(x, y)) != isWhite(bi.getRGB(x, y))) {  
                        count++;  
                        if (count >= min)  
                            break Label1;  
                    }  
                }  
            }  
            if (count < min) {  
                min = count;  
                result = map.get(bi);  
            }  
        }  
        return result;  
    }  
  
    public static String getAllOcr(String file) throws Exception {  
        BufferedImage img = removeBackgroud(file);  
        List<BufferedImage> listImg = splitImage(img);  
        
        Map<BufferedImage, String> map = loadTrainData();  
        String result = "";  
        for (BufferedImage bi : listImg) {  
            result += getSingleCharOcr(bi, map);  
        }  
//        ImageIO.write(img, "JPG", new File("result2//" + result + ".jpg"));  
        return result;  
    }  
    
    public static String getAllOcr( BufferedImage img) throws Exception {  
         img = removeBackgroud(img);  
        List<BufferedImage> listImg = splitImage(img);  
        
        Map<BufferedImage, String> map = loadTrainData();  
        String result = "";  
        for (BufferedImage bi : listImg) {  
            result += getSingleCharOcr(bi, map);  
        }  
//        ImageIO.write(img, "JPG", new File("result2//" + result + ".jpg"));  
        return result;  
    }  
  
    //"https://service.htsc.com.cn/service/pic/verifyCodeImage.jsp?ran=0.5" 
    public static void downloadImage(String url) {  
        HttpClient httpClient = HttpClientBuilder.create().build();
        HttpGet getMethod = null;  
        for (int i = 0; i < 100; i++) {  
			getMethod = new HttpGet(url + "?random=0.2" + (2000 + i));
            try {  
                // 执行getMethod  
            	HttpResponse response = httpClient.execute(getMethod);  
//                if (response. != HttpStatus.SC_OK) {  
//                    System.err.println("Method failed: "  
//                            + getMethod.getStatusLine());  
//                }  
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
                getMethod.releaseConnection();  
            }  
        }  
    }  
  
    public static void trainData() throws Exception {  
        File dir = new File("temp");  
        File[] files = dir.listFiles();  
        for (File file : files) {  
        	if("kap4.jpg".equals(file.getName())) {
        		System.out.println("sss");
        	}
        	boolean isDebug = true;
            BufferedImage img = removeBackgroud("temp//" + file.getName());
            if(isDebug) {
            ImageIO.write(img, "JPG", new File("removebackground//"  
                    + file.getName() 
                    + ".jpg"));  
            }
            
            List<BufferedImage> listImg = splitImage(img);  
            if (listImg.size() == 5) {  
                for (int j = 0; j < listImg.size(); ++j) {  
                    ImageIO.write(listImg.get(j), "JPG", new File("train2//"  
                            + file.getName().charAt(j) + "-" + (index++)  
                            + ".jpg"));  
                }  
            }  
        }  
    }  
  
    
    /** 
     * @param args 
     * @throws Exception 
     */  
    public static void main(String[] args) throws Exception {  
    	String  url = "https://trade.gf.com.cn/yzm.jpgx";
//    	downloadImage(url);
    	trainData();
    	
//    	File dir = new File("temp");  
//        File[] files = dir.listFiles();  
//        for (File file : files) {  
//        	  String text = getAllOcr(file.getPath());  
//              System.out.println(file.getName() + "= " + text);
//        }
    }  
}  
