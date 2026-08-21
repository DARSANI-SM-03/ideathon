from app.ai.behavior_engine import behavior_engine

res1 = behavior_engine.classify_with_confidence("Antigravity IDE.exe", "StudIQ_02 - Antigravity IDE - Implementation Plan")
res2 = behavior_engine.classify_with_confidence("chrome.exe", "LeetCode - Problem 1 - Google Chrome")
res3 = behavior_engine.classify_with_confidence("chrome.exe", "Instagram - Feed - Google Chrome")
res4 = behavior_engine.classify_with_confidence("steam.exe", "Steam Store")

print("Antigravity IDE ->", res1)
print("LeetCode        ->", res2)
print("Instagram       ->", res3)
print("Steam           ->", res4)
