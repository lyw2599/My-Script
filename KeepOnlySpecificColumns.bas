Sub KeepOnlySpecificColumns()
    Dim ws As Worksheet
    Dim columnsToKeep As Variant
    Dim lastCol As Long, i As Long
    
    ' 设置要保留的列（可以是列字母或数字）
    columnsToKeep = Array("B", "D", "F") ' 示例：只保留 B、D、F 列
    
    ' 操作的活动工作表（或指定工作表：Set ws = ThisWorkbook.Sheets("Sheet1")）
    Set ws = ActiveSheet
    
    ' 获取最后一列的列号
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    ' 从右到左遍历所有列（避免删除后列号变化）
    For i = lastCol To 1 Step -1
        ' 检查当前列是否不在保留列表中
        If Not IsInArray(ws.Columns(i).Address(False, False), columnsToKeep) Then
            ws.Columns(i).Delete
        End If
    Next i
    
    MsgBox "仅保留 B、D、F 列，其他列已删除！"
End Sub

' 辅助函数：检查值是否在数组中
Function IsInArray(val As String, arr As Variant) As Boolean
    Dim item As Variant
    For Each item In arr
        If UCase(val) = UCase(item) Then
            IsInArray = True
            Exit Function
        End If
    Next
    IsInArray = False
End Function
