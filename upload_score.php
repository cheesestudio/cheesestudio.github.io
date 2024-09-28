<?php  

// Elo算法的简化参数  
$K_FACTOR = 32; // K因子，决定评分变化的幅度  
$INITIAL_RATING = 1500; // 初始评分  
  
function updateEloRating($winner, $loser, &$ratings, $K_FACTOR = 32,$INITIAL_RATING = 1500) {  
    $winnerRating = $ratings[$winner] ?? $INITIAL_RATING;  
    $loserRating = $ratings[$loser] ?? $INITIAL_RATING;  
  
    $expectedWinner = 1 / (1 + pow(10, (($loserRating - $winnerRating) / 400)));  
    $eloGain = $K_FACTOR * (1 - $expectedWinner);  
  
    $expectedLoser = 1 / (1 + pow(10, (($winnerRating - $loserRating) / 400)));  
    $eloLoss = $K_FACTOR * ($expectedLoser - 1);  
  
    $ratings[$winner] = $winnerRating + $eloGain;  
    $ratings[$loser] = $loserRating + $eloLoss;  
}  
// 假设这是通过GET请求提交数据的处理页面  
if ($_SERVER["REQUEST_METHOD"] == "GET") {  
    // 获取玩家名字和分数  
    $player1 = isset($_GET['player1']) ? $_GET['player1'] : '';  
    $player2 = isset($_GET['player2']) ? $_GET['player2'] : '';  
    $score1 = isset($_GET['score1']) ? (int)$_GET['score1'] : 0;  
    $score2 = isset($_GET['score2']) ? (int)$_GET['score2'] : 0;  
    $winner = ($score1 > $score2) ? $player1 : $player2;  
    $loser = ($winner == $player1) ? $player2 : $player1;  
    $hash = isset($_GET['hash']) ? $_GET['hash'] : '';  
  
    // 它需要player1, player2, score1, score2和预期的hash作为参数  
    $expectedHash = calculateHash($player1 , $player2 , $score1 , $score2 ); // 示例hash生成  
    //echo $expectedHash;
    if ($hash !== $expectedHash) 
    {  
        die("Hash验证失败！");  
    }  
        // 检查最近10条记录中是否已存在该记录  
    $recentRecordsFilePath = 'recent_records.txt';  
    $isDuplicate = false;  
    if (file_exists($recentRecordsFilePath)) {  
        $lines = file($recentRecordsFilePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);  
        $recentRecords = array_slice($lines, -10); // 获取最近10条记录  
  
        $recordToCheck = implode(';', [$player1, $player2, $score1, $score2, $hash]);  
        if (in_array($recordToCheck, $recentRecords)) {  
            $isDuplicate = true;  
        }  
    }  
  
    if ($isDuplicate) {  
        die("上传的数据与最近10条记录重复！");  
    }  
  
    // ... 更新或添加两位玩家的分数（保持不变，但注意我们不再直接写入文件） ...  
  
    // 将新记录添加到最近记录文件中  
    $newRecord = implode(';', [$player1, $player2, $score1, $score2, $hash]) . PHP_EOL;  
    file_put_contents($recentRecordsFilePath, $newRecord, FILE_APPEND | LOCK_EX);

    // 更新或添加两位玩家的分数  
    $filePath = 'scores.txt'; 
    $updatedContent = [];  
    $playersScores = [];
    // 读取文件内容  
    if (file_exists($filePath)) 
    {  
        $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);  
          
        foreach ($lines as $line) 
        {  
            list($name, $score) = explode(';', $line, 2);  
            $playersScores[$name] = $score;  
        }  
  
        // 更新分数  
        // 假设根据净胜场次调整K因子  
        $netWins = abs($score1 - $score2);  
        $adjustedKFactor = $K_FACTOR * (1 + $netWins / 4); // 假设每多赢一场，K因子增加20%  斯诺克就是 8倍
  
        // 使用调整后的K因子来更新评分  
        updateEloRating($winner, $loser, $playersScores, $adjustedKFactor);
        // 如果需要处理平局，可以在这里添加逻辑    
          // 将所有分数（包括新添加的）复制到$updatedScores以便排序  
        $updatedScores = $playersScores;  
    } 
    else 
    {  
        // 如果文件不存在，初始化分数  
        $playersScores[$player1] = $INITIAL_RATING;  
        $playersScores[$player2] = $INITIAL_RATING;  

        $updatedScores = $playersScores;  
    }  
        arsort($updatedScores);  
  
        // 准备更新后的内容  
        $updatedContent = [];  
        foreach ($updatedScores as $name => $score) 
        {  
        $updatedContent[] = $name . ';' . $score;  
        }   
    // 将更新后的内容写回文件  
    file_put_contents($filePath, implode(PHP_EOL, $updatedContent));  
  
    // 反馈给用户  
    echo "分数已保存！";  
} 
else 
{  
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