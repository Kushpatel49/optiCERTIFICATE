"""
Table utility functions for Word document generation
"""

from docx.shared import Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from config import TABLE_WIDTH_INCHES, SR_NO_COLUMN_WIDTH_INCHES


def set_cell_border(cell, **kwargs):
    """Set cell borders"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    
    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'tc{}'.format(edge.capitalize())
            element = OxmlElement('w:{}'.format(tag))
            element.set(qn('w:val'), 'single')
            element.set(qn('w:sz'), '4')
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), '000000')
            tcPr.append(element)


def add_table_with_borders(doc, rows, cols):
    """
    Add table with borders and fixed width - optimized for Microsoft Word compatibility
    
    Args:
        doc: Document object
        rows: Number of rows
        cols: Number of columns
        
    Returns:
        Table object with proper formatting
    """
    table = doc.add_table(rows=rows, cols=cols)
    table.style = 'Table Grid'
    table.autofit = False  # Disable autofit to set fixed width
    
    # Set table width
    table.width = Inches(TABLE_WIDTH_INCHES)
    
    # Smart column width management for Microsoft Word compatibility
    # Sr. No. column gets fixed width, remaining columns share the rest proportionally
    if cols > 0:
        total_width_inches = TABLE_WIDTH_INCHES
        sr_no_width_inches = SR_NO_COLUMN_WIDTH_INCHES
        remaining_width_inches = total_width_inches - sr_no_width_inches
        
        # Calculate width for other columns in inches
        if cols > 1:
            other_col_width_inches = remaining_width_inches / (cols - 1)
        else:
            other_col_width_inches = remaining_width_inches
        
        # Set widths using Inches objects - Word handles this better
        sr_no_width = Inches(sr_no_width_inches)
        other_col_width = Inches(other_col_width_inches)
        
        # For Microsoft Word compatibility: set both column and cell widths
        # Setting column width first, then individual cells for maximum compatibility
        for i, column in enumerate(table.columns):
            if i == 0:  # First column (Sr. No.)
                column.width = sr_no_width
            else:
                column.width = other_col_width
        
        # Also set width for each cell individually (Word respects this better)
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                if i == 0:  # First column (Sr. No.)
                    cell.width = sr_no_width
                else:
                    cell.width = other_col_width
    
    return table


def enforce_sr_no_column_width(table, headers, width=Inches(SR_NO_COLUMN_WIDTH_INCHES)):
    """
    Standardized column-width calculation for all annexure tables.

    - If the first header is a variation of "Sr. No.", the first column is kept
      at SR_NO_COLUMN_WIDTH_INCHES and the remaining columns share the rest of
      TABLE_WIDTH_INCHES proportionally based on header text length.
    - If there is no "Sr. No." column (e.g. the summary table), the full table
      width is distributed proportionally, but we guarantee that the first
      column gets a minimum share so its text (e.g. "Particulars") does not wrap.

    This function is called *after* headers are set so it can infer sensible
    widths from the header content alone.
    """
    if not headers or not table.columns:
        return

    total_width_inches = TABLE_WIDTH_INCHES

    # Normalize first header for Sr. No. detection
    first_header = (headers[0] or "").replace("\n", " ").strip().lower()
    has_sr_no = first_header.startswith("sr.") or "sr" in first_header and "no" in first_header

    # Determine available width and starting column index for proportional sizing
    col_start_index = 0
    widths_inches = []

    if has_sr_no:
        # Fixed Sr. No. column width
        sr_no_width_inches = SR_NO_COLUMN_WIDTH_INCHES
        widths_inches.append(sr_no_width_inches)
        remaining_width_inches = max(total_width_inches - sr_no_width_inches, 0.1)
        col_start_index = 1
        headers_for_sizing = headers[1:]
    else:
        remaining_width_inches = total_width_inches
        headers_for_sizing = headers

    if not headers_for_sizing:
        # Only Sr. No. column; just apply fixed width
        for row in table.rows:
            row.cells[0].width = width
        table.columns[0].width = width
        return

    # Use header text length as a proxy for required width, with a reasonable minimum.
    min_len = 10
    text_lengths = [max(len(h or ""), min_len) for h in headers_for_sizing]
    total_len = float(sum(text_lengths)) or 1.0

    # Initial proportional widths
    prop_widths = [remaining_width_inches * (l / total_len) for l in text_lengths]

    # If there is no Sr. No. column, enforce a minimum share for the first column
    if not has_sr_no:
        min_first_ratio = 0.25  # First column gets at least 25% of total width
        min_first_width = total_width_inches * min_first_ratio
        if prop_widths[0] < min_first_width:
            # Reduce other columns proportionally to keep total width constant
            excess = min_first_width - prop_widths[0]
            other_total = remaining_width_inches - prop_widths[0]
            if other_total > 0:
                scale = max((other_total - excess) / other_total, 0.1)
                for i in range(1, len(prop_widths)):
                    prop_widths[i] *= scale
            prop_widths[0] = min_first_width

    widths_inches.extend(prop_widths)

    # Apply widths to table columns and cells
    for col_idx, column in enumerate(table.columns):
        if col_idx < len(widths_inches):
            col_width = Inches(widths_inches[col_idx])
            column.width = col_width
            for row in table.rows:
                row.cells[col_idx].width = col_width


