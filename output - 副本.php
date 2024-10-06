<?php  
$filePath = 'recent_records.txt';  
$lineNumber = 1; // 初始化序号计数器    

if (file_exists($filePath)) {  
    $content = file_get_contents($filePath);  
  
    // 这里不直接替换空格为不换行空格，因为文件通常不存储HTML内容  
    // 如果需要在显示时处理空格，可以在输出到HTML时替换  
  
    $lines = explode("\n", $content);  
  
    $processedContent = '';  
  
    foreach ($lines as $line) {  
        $parts = explode(";", $line);  
  
        if (count($parts) >= 2) {  
            // 假设$parts[0]是玩家名字，$parts[1]是分数  
            $playerName = $parts[0]; 
            $score = intval($parts[1]); // 将分数转换为整数  
  
            $playerName = str_replace(" ", " ", $playerName);
            // 重新组合字符串，这里为了演示，我们不做空格的特殊处理  
            // 如果需要在HTML中显示不换行空格，可以在输出时替换空格为&nbsp;  
            $processedContent .= $lineNumber . "." .  $playerName . " " . $score . "\n";  
            $lineNumber++; // 增加序号计数器  
        }  
    }  
  
    // 输出处理后的内容  
    echo $processedContent;  
} else {  
    echo "<h3>文件不存在</h3>";  
}  
?>