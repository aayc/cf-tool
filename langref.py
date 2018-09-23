
def getMultilineBeginComment(file_ext):
	return {
		"py": "'''",
		"cpp": "/*",
		"js": "/*",
		"hs": "---"
	}[file_ext]

def getMultilineEndComment(file_ext):
	return {
		"py": "'''",
		"cpp": "*/",
		"js": "*/",
		"hs": "---"
	}[file_ext]