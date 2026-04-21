#reports/view.py
#Student 5 - reports module
#generates pdf and excel reports from the shared database.

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone

# ReportLab for PDF generation

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


#OpenPyXl fro excel generation
import openpyxl
from openpyxl.styles import Font, PatternFill,Alignment, Border, Side
from openpyxl.utils import get_column_letter

import datetime

#---------------------------------------------------------------------
#imprt shared models
#models are created by the Group (core/teams/organisation apps).
#----------------------------------------------------------------------

try: 
    from teams.models import Team #student 1's app
    from organization.models import Department #student 2's app
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    Team = None
    Department = None


#-------------------------------
#HELPER: GET REPORT DATA SAFELY
#-------------------------------

def get_report_data():
    """
    Collect all statistics needed for reports.
    Returns a dict with counts and querysets.
    Falls back to empty data if models are not yet available.
    """
    if not MODELS_AVAILABLE:
        return {
            'total_teams' : 0,
            'total_department' : 0,
            'teams_without_managers' : 0,
            'teams' : [],
            'departments' : [] ,
            'teams_no_manager_list' : [],
            'generated_at' : timezone.now(),
        }
    
    teams = Team.objects.select_related('department', 'manager').all()
    departments = Department.objects.annotate(team_count = Count('team')).all()

    #Teams with no manager assigned
    #Ajust field name 'manager' to match group's actual Team model field
    teams_no_manager = teams.filter(
        Q(manager__isnull = True) | Q(manager='')
    )

    return {
        'total_teams' : teams.count(),
        'total_departments' : departments.count(),
        'teams_without_managers' : teams_no_manager.count(),
        'teams' : teams,
        'departments' : departments,
        'teams_no_manager_list' : teams_no_manager,
        'generated_at' : timezone.now(),
    }

#---------------------------------------------------
# VIEW 1: Reports Dashboard (HTML pg)
#---------------------------------------------------

@login_required
def reports_dashboard(request):
    """
    Main report landing pg
    shows summary stats and buttons to download PDF/ Excel.
    """

    data = get_report_data()
    context = {
        'title' : 'Reports',
        'total_teams' : data['total_teams'],
        'total_departments' : data['total_departments'],
        'teams_without_managers' : data['teams_without_managers'],
        'teams' : data['teams'],
        'departments' : data['departments'],
        'teams_no_manager_list' : data['teams_no_manager_list'],
        'generated_at' : data['generated_at'],
    }

    return render(request, 'reports/dashboard.html', context)


#-----------------------------------------------------
# VIEW 2: generated PDF report
#-----------------------------------------------------

@login_required
def generate_pdf_report(request):
    """
    generates and downloads a PDF report of all teams
    covers: total teams, summary, teams without managers.
    """
    data = get_report_data()

    # set up the HTTP response as a PDF file
    response = HttpResponse(content_type = 'application/pdf')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="team_report_{timestamp}.pdf"'

    #create the pdf documents
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    #Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1a237e'),
        spaceBefore=14,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    story = [] # list of flowable elements


    #---Title---
    story.append(Paragraph("Broadcast Company Engineering", title_style))
    story.append(Paragraph("Team Registry Report", title_style))
    story.append(Paragraph(
        f"Generated: {data['generated_at'].strftime('%d %B %Y, %H:%M')} | "
        f"Prepared by: {request.user.get_full_name() or request.user.userame}",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a237e')))
    story.append(Spacer(1, 0.4 * cm))

    #--Section 1: Summary Statistics -- 
    story.append(Paragraph("1. Summary", heading_style))

    summary_data = [
        ['Metric', 'Value'],
        ['Total Engineering Teams', str(data['total_teams'])],
        ['Total Departments', str(data['total_departments'])],
        ['Teams Without a Manager', str(data['teams_without_managers'])],
        ['Report Date', data['generated_at'].strftime('%d/%m/%Y')],
    ]

    summary_table = Table(summary_data, colWidths=[10 * cm, 6 * cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1,0), colors.white),
        ('FONTNAME', (0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0), 11),
        ('ALIGN', (0,0),(-1,-1), 'LEFT'),
        ('FONTNAME', (0,1),(-1,-1),'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1),(-1,-1, [colors.HexColor('#e8eaf6')])),
        ('GRID', (0,0),(-1,-1),0.5, colors.HexColor('#9fa8da')),
        ('LEFTPADDING', (0,0),(-1,-1), 8),
        ('RIGHTPADDING', (0,0),(-1,-1),8),
        ('TOPPADDING' (0,0),(-1,-1),6),
        ('BOTTOMPADDING', (0,0),(-1,-1),6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1,0.5 * cm))

    #--Section 2: All Teams--
    story.append(Paragraph("2. All Engineering Teams", heading_style))

    if data['teams']:
        teams_data = [['Team Name', 'Department', 'Manager', 'Members']]
        for team in data['teams']:
            dept_name = getattr(getattr(team, 'department', None), 'name', 'N/A')
            manager = getattr(team, 'manager', None)
            if manager:
                manager_name = str(manager)
            else:
                manager_name = 'Not Assigned'
            member_count = str(getattr(team, 'members', team.__class__.objects).count()
                               if hasattr(team, 'members') else 'N/A')
            teams_data.append([
                getattr(team, 'name', str(team)),
                dept_name,
                manager_name,
                member_count,
            ])

        col_widths = [5 * cm, 4 * cm, 5 * cm, 3 * cm]
        teams_table = Table(teams_data, colWidths=col_widths, repeatRows=1)
        teams_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0,0),(-1,0), colors.white),
            ('FONTNAME', (0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,0), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME',(0,1),(-1,-1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8eaf6')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9fa8da')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(teams_table)
    else:
        story.append(Paragraph("No teams found in the database.", normal_style))
    
    story.append(Spacer(1, 0.5 * cm))


    #--Section 3: Teams without Managers--
    story.append(Paragraph("3. Teams Without Managers", heading_style))
    story.append(Paragraph(
        "The following teams currently have no manager assigned and require attention: ", normal_style
    ))

    if data['teams_no_manager_list']:
        no_mgr_data = [['Team Name', 'Department', 'Status']]
        for team in data['teams_no_manager_list']:
            dept_name = getattr(getattr(team, 'department', None), 'name', 'N/A')
            no_mgr_data.append([
                getattr(team, 'name', str(team)),
                dept_name,
                'Manager Required'
            ])

        no_mgr_table = Table(no_mgr_data, colWidths=[6 * cm, 5 * cm, 6 * cm])
        no_mgr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#b71c1c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffebee')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ef9a9a')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        story.append(no_mgr_table)

    else:
        story.append(Paragraph(
            "All teams cureently have a manager assigned. ", normal_style
        ))


    #--Footer--
    story.append(Spacer(1,1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Paragraph(
        "Broadcast Company Engineering - Confidential - Generated by Team Resgistry Portal", subtitle_style
    ))


    doc.build(story)
    return response
#------------------------------------------------------
# VIEW 3: Generate Excel Report
#------------------------------------------------------

@login_required
def generate_excel_report(request):
    """
    generates and downloads an excel (.xlsx) report.
    contains multiple sheets: summary, all teams, teams without managers.
    """
    data = get_report_data()
    wb = openpyxl.Workbook()

    #--Define reusable styles--
    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_fill_blue = PatternFill(start_color='1A237E', end_color='1A237E', fill_type='solid')
    header_fill_red = PatternFill(start_color='B71C1C', end_color='B71C1C', fill_type='solid')
    row_fill_alt = PatternFill(start_color='E8EAF6', end_color='E8EAF6', fill_type='solid')
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')
    thin_border = Border(
        left=Side(style='thin', color='9FA8DA'),
        right=Side(style='thin', color='9FA8DA'),
        top=Side(style='thin', color='9FA8DA'),
        bottom=Side(style='thin', color='9FA8DA'),
    )

    def style_header_row(ws, row_num, col_count, fill=None):
        fill = fill or header_fill_blue
        for col in range(1, col_count +1):
            cell = ws.cell(row=row_num, column = col)
            cell.font = header_font
            cell.fill = fill
            cell.alignment = center_align
            cell.border = thin_border
    
    def style_data_row(ws, row_num, col_count, alternate = False):
        for col in range(1, col_count + 1):
            cell = ws.cell(row=row_num, column = col)
            cell.alignment = left_align
            cell.border = thin_border
            if alternate:
                cell.fill = row_fill_alt
    
    def auto_width(ws):
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max_len + 4, 50)


    #-----------------------------------------------
    # SHEET 1: Summary
    #-----------------------------------------------
    ws1= wb.active
    ws1.title = "Summary"

    ws1.merge_cells('A1:C1')
    title_cell = ws1['A1']
    title_cell.value = "Broadcast Company - Engineering Team Report"
    title_cell.font = Font(bold=True, size=14, color='1A237E')
    title_cell.alignment = center_align

    ws1.merge_cells('A2:C2')
    ws1['A2'].value = f"Generated: {data['generated_at'].strftime('%d %B %Y, %H:%M')}"
    ws1['A2'].alignment = center_align
    ws1['A2'].font = Font(italic=True, color='757575')
 
    ws1.append([])  # blank row
 
    headers = ['Metric', 'Value', 'Notes']
    ws1.append(headers)
    style_header_row(ws1, ws1.max_row, 3)
 
    rows = [
        ('Total Engineering Teams', data['total_teams'], 'All active teams in the registry'),
        ('Total Departments', data['total_departments'], 'Departments with at least one team'),
        ('Teams Without Manager', data['teams_without_managers'], 'Requires immediate attention'),
        ('Report Generated By', request.user.get_full_name() or request.user.username, ''),
        ('Report Date', data['generated_at'].strftime('%d/%m/%Y'), ''),
    ]
    for i, row in enumerate(rows):
        ws1.append(list(row))
        style_data_row(ws1, ws1.max_row, 3, alternate=(i % 2 == 1))


    auto_width(ws1)
    ws1.row_dimensions[1].height = 30
    ws1.row_dimensions[4].height = 22

    #-------------------------------
    # SHEET 2: All teams
    #-------------------------------
    ws2= wb.create_sheet("All Teams")

    ws2.merge_cells('A1:E1')
    ws2['A1'].value = "All Engineering teams"
    ws2['A1'].font = Font(bold=True, size=13, color='1A237E')
    ws2['A1'].alignment = center_align
    ws2.row_dimensions[1].height =25
    ws2.append([])
    headers2 = ['Team Name', 'Department', 'Manager', 'No. of Members', 'Purpose/Description']
    ws2.append(headers2)
    style_header_row(ws2, ws2.max_row, 5)
 
    if data['teams']:
        for i, team in enumerate(data['teams']):
            dept_name = getattr(getattr(team, 'department', None), 'name', 'N/A')
            manager = getattr(team, 'manager', None)
            manager_name = str(manager) if manager else 'Not Assigned'
            members = getattr(team, 'members', None)
            member_count = members.count() if members is not None else 'N/A'
            description = getattr(team, 'description', '') or getattr(team, 'purpose', '') or ''
 
            ws2.append([
                getattr(team, 'name', str(team)),
                dept_name,
                manager_name,
                member_count,
                description[:100] + '...' if len(str(description)) > 100 else description,
            ])
            style_data_row(ws2, ws2.max_row, 5, alternate=(i % 2 == 1))
    else:
        ws2.append(['No teams found.', '', '', '', ''])
 
    auto_width(ws2)
 
    # ════════════════════════════════
    #  SHEET 3: Teams Without Managers
    # ════════════════════════════════
    ws3 = wb.create_sheet("Teams Without Managers")
 
    ws3.merge_cells('A1:D1')
    ws3['A1'].value = "⚠ Teams Without Managers – Action Required"
    ws3['A1'].font = Font(bold=True, size=13, color='B71C1C')
    ws3['A1'].alignment = center_align
    ws3.row_dimensions[1].height = 25
    ws3.append([])
 
    headers3 = ['Team Name', 'Department', 'Status', 'Action Needed']
    ws3.append(headers3)
    style_header_row(ws3, ws3.max_row, 4, fill=header_fill_red)
 
    if data['teams_no_manager_list']:
        alert_fill = PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid')
        for team in data['teams_no_manager_list']:
            dept_name = getattr(getattr(team, 'department', None), 'name', 'N/A')
            ws3.append([
                getattr(team, 'name', str(team)),
                dept_name,
                'No Manager Assigned',
                'Assign a manager immediately',
            ])
            row_num = ws3.max_row
            for col in range(1, 5):
                cell = ws3.cell(row=row_num, column=col)
                cell.fill = alert_fill
                cell.border = thin_border
                cell.alignment = left_align
    else:
        ws3.append(['✓ All teams have managers assigned.', '', '', ''])
 
    auto_width(ws3)
 
    # ── Save and return ──
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="team_report_{timestamp}.xlsx"'
    wb.save(response)
    return response
 
 
# ─────────────────────────────────────────────
#  VIEW 4: Department Report (bonus page)
# ─────────────────────────────────────────────
@login_required
def department_report(request):
    """
    Shows a per-department breakdown on screen.
    """
    data = get_report_data()
    context = {
        'title': 'Department Report',
        'departments': data['departments'],
        'generated_at': data['generated_at'],
    }
    return render(request, 'reports/department_report.html', context)
 