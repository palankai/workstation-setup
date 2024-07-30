# Disable press and hold for keys in favor of key repeat
defaults write -g ApplePressAndHoldEnabled -bool false

# Don't store quick time history
defaults write com.apple.QuickTimePlayerX NSRecentDocumentsLimit 0
defaults delete com.apple.QuickTimePlayerX.LSSharedFileList RecentDocuments
defaults write com.apple.QuickTimePlayerX.LSSharedFileList RecentDocuments -dict-add MaxAmount 0
