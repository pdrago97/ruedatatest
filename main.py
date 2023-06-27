from fastapi import FastAPI, UploadFile, HTTPException, File
from typing import List

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.endswith('.txt'):
        contents = await file.read()
        contents = contents.replace(b'\r\n', b'\n')
        contents = contents.decode('utf-8').split('\n')
        if not all(len(line) == 3 for line in contents):
            raise HTTPException(status_code=400, detail="Invalid file format. All lines should contain exactly 3 characters.")
        secret_code = determine_secret_code(contents)
        return {"filename": file.filename, "secret_code": secret_code}
    else:
        raise HTTPException(status_code=400, detail="Invalid file format. Only .txt files are accepted.")

@app.get("/")
async def root():
    return {"message": "Hello World"}


from collections import defaultdict

def determine_secret_code(lines: List[str]) -> str:
    # Create a graph where each node points to all nodes that can follow it
    graph = defaultdict(list)
    for line in lines:
        for i in range(len(line) - 1):
            if line[i+1] not in graph[line[i]]:
                graph[line[i]].append(line[i+1])

    # Find all nodes that have no incoming edges
    start_nodes = set(graph.keys())
    for edges in graph.values():
        start_nodes -= set(edges)

    # There should be exactly one start node
    assert len(start_nodes) == 1
    start_node = start_nodes.pop()

    # Perform a depth-first search to find the shortest path that visits all nodes
    path = []
    stack = [(start_node, [start_node])]
    while stack:
        node, path = stack.pop()
        for next_node in graph[node]:
            if next_node not in path:
                stack.append((next_node, path + [next_node]))
    return ''.join(path)
