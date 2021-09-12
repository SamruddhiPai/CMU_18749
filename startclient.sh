
osascript -e 'tell app "Terminal"
    do script "cd /Users/riturajsingh/BigFolder/courses/2_18749_Reliable_DS/CMU_18749 && python3 client1.py"
    do script "cd /Users/riturajsingh/BigFolder/courses/2_18749_Reliable_DS/CMU_18749 && python3 client2.py"
    do script "cd /Users/riturajsingh/BigFolder/courses/2_18749_Reliable_DS/CMU_18749 && python3 client3.py"
    do script "cd /Users/riturajsingh/BigFolder/courses/2_18749_Reliable_DS/CMU_18749 && python3 status.py"
end tell'
