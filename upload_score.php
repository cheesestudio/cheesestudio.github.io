<?php  
// 假设这是通过GET请求提交数据的处理页面  
if ($_SERVER["REQUEST_METHOD"] == "GET") {  
    // 获取玩家名字和分数  
    $player1 = isset($_GET['player1']) ? $_GET['player1'] : '';  
    $player2 = isset($_GET['player2']) ? $_GET['player2'] : '';  
    $score1 = isset($_GET['score1']) ? (int)$_GET['score1'] : 0;  
    $score2 = isset($_GET['score2']) ? (int)$_GET['score2'] : 0;  
    $hash = isset($_GET['hash']) ? $_GET['hash'] : '';  
  
    // 假设这里有一个函数validateHash，用于验证hash是否有效  
    // 它需要player1, player2, score1, score2和预期的hash作为参数  
    // 这里只是一个示例，实际验证逻辑需根据具体算法实现  
    $expectedHash = calculateHash($player1 , $player2 , $score1 , $score2 ); // 示例hash生成  
    //echo $expectedHash;
    if ($hash !== $expectedHash) {  
        die("Hash验证失败！");  
    }  
  
    $filePath = 'scores.txt';  
  
    // 更新或添加两位玩家的分数  
    $updatedContent = [];  
  
    // 读取文件内容  
    if (file_exists($filePath)) {  
        $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);  
        $playersScores = [];  
        foreach ($lines as $line) {  
            list($name, $score) = explode(';', $line, 2);  
            $playersScores[$name] = $score;  
        }  
  
        // 更新分数  
        if (isset($playersScores[$player1])) {  
            $score1 += intval($playersScores[$player1]);  
        }  
        if (isset($playersScores[$player2])) {  
            $score2 += intval($playersScores[$player2]);  
        }  
  
        $updatedContent[] = $player1 . ';' . $score1;  
        $updatedContent[] = $player2 . ';' . $score2;  
  
        // 如果需要，可以移除已存在的旧条目（这里简单起见不处理）  
    } else 
    {  
        // 如果文件不存在，直接添加  
        $updatedContent[] = $player1 . ';' . $score1;  
        $updatedContent[] = $player2 . ';' . $score2;  
    }  
        arsort($playersScores);  
  
        // 准备更新后的内容  
        foreach ($playersScores as $name => $score) 
        {  
            $updatedContent[] = $name . ';' . $score;  
        }  
    // 将更新后的内容写回文件  
    file_put_contents($filePath, implode(PHP_EOL, $updatedContent));  
  
    // 反馈给用户  
    echo "分数已保存！";  
} else {  
    // 如果不是GET请求，则显示错误消息（可选）  
    echo "无效的请求方式，请使用GET请求。";  
}

function calculateHash($player1, $player2, $score1, $score2, $hashKey = "CheeseIsTheHashKeyForNoReason") {  
    // 将所有参数按照指定顺序拼接成一个字符串  
    $data = $player1 . $player2 . $score1 . $score2 . $hashKey;  
  
    // 使用md5()函数计算字符串的MD5 hash，该函数默认使用UTF-8（对于ASCII字符串）  
    $hash = md5($data);  
  
    return $hash;  
}  