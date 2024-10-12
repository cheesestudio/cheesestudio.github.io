<?php
$filePath = 'recent_records.txt';

// 检查文件是否存在  
if (file_exists($filePath)) {
    // 使用file_get_contents()函数读取文件内容  
    $fileContent = file_get_contents($filePath);

    // 输出文件内容  
    echo $fileContent;
} else {
    // 如果文件不存在，输出错误信息  
    echo "Error: The file '$filePath' does not exist.";
}
?>