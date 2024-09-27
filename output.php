<?php  
// 设置文本文件的路径  
$filePath = 'scores.txt';  
  
// 检查文件是否存在  
if (file_exists($filePath)) {  
    // 读取文件内容  
    $content = file_get_contents($filePath);  
      
    // 替换中文分号为一个空格（如果需要）  
    $content = str_replace(";", " ", $content);  

    $lines = explode("\n", $content);  
  
    // 初始化一个空数组来存储转换后的数据  
    $scoresArray = [];  
  
    // 遍历每一行  
    foreach ($lines as $line) 
    {  
        // 假设每行格式为 "名字 分数"，使用空格分割  
        $parts = explode(";", $line);  

              // 检查是否至少有两个部分（名字和分数）  
        if (count($parts) >= 2) 
        {  
            // 尝试将分数转换为整数  
            $score = intval($parts[1]);  
        }
    // 去除内容中连续的多个换行，只保留一个换行  
    $content = preg_replace("/\n{2,}/", "\n", $content);  
      
    // 输出文件内容  
    echo "<pre>" . htmlspecialchars($content) . "</pre>"; // 直接使用 <pre> 标签保持格式  
} 
else 
{  
    echo "<h3>文件不存在</h3>";  
}  
?>