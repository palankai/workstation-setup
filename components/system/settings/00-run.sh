# Enable or disable press and hold for keys in favor of key repeat
defaults write -g ApplePressAndHoldEnabled -bool false || true

# Don't store quick time history
defaults write com.apple.QuickTimePlayerX NSRecentDocumentsLimit 0  || true
defaults delete com.apple.QuickTimePlayerX.LSSharedFileList RecentDocuments || true
defaults write com.apple.QuickTimePlayerX.LSSharedFileList RecentDocuments -dict-add MaxAmount 0 || true
