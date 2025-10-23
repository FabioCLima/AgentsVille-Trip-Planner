#!/usr/bin/env python3
"""
Script avançado para análise detalhada dos itinerários gerados.
"""

import json
import re
from typing import Dict, List, Any, Optional

def extract_detailed_itinerary_data(notebook_path: str) -> Dict[str, Any]:
    """Extrai dados detalhados do itinerário do notebook."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    data = {
        'initial_itinerary': {
            'total_cost': None,
            'calculated_cost': None,
            'activities': [],
            'days': [],
            'warnings': []
        },
        'revised_itinerary': {
            'total_cost': None,
            'calculated_cost': None,
            'activities': [],
            'days': [],
            'warnings': []
        },
        'evaluation_results': {
            'initial_passed': False,
            'revised_passed': False,
            'initial_failures': [],
            'revised_failures': []
        }
    }
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code' and 'outputs' in cell:
            for output in cell['outputs']:
                if output.get('output_type') == 'stream':
                    text = ''.join(output.get('text', []))
                    
                    # Extrair informações de custo
                    cost_pattern = r'Stated total_cost \((\d+)\) doesn\'t match calculated total \((\d+)\)'
                    cost_match = re.search(cost_pattern, text)
                    if cost_match:
                        stated_cost = int(cost_match.group(1))
                        calculated_cost = int(cost_match.group(2))
                        
                        if 'Initial' in text or 'initial' in text:
                            data['initial_itinerary']['total_cost'] = stated_cost
                            data['initial_itinerary']['calculated_cost'] = calculated_cost
                        elif 'Revised' in text or 'revised' in text:
                            data['revised_itinerary']['total_cost'] = stated_cost
                            data['revised_itinerary']['calculated_cost'] = calculated_cost
                    
                    # Extrair atividades por data
                    if 'Date: 2025-' in text:
                        lines = text.split('\n')
                        current_date = None
                        for line in lines:
                            if line.startswith('Date: '):
                                current_date = line.replace('Date: ', '').strip()
                                if current_date not in [d['date'] for d in data['initial_itinerary']['days']]:
                                    data['initial_itinerary']['days'].append({'date': current_date, 'activities': []})
                            elif 'activity_id' in line and current_date:
                                # Esta é uma linha de atividade
                                activity_match = re.search(r'event-\d{4}-\d{2}-\d{2}-\d+', line)
                                if activity_match:
                                    activity_id = activity_match.group(0)
                                    for day in data['initial_itinerary']['days']:
                                        if day['date'] == current_date:
                                            day['activities'].append(activity_id)
                                            break
                    
                    # Extrair resultados de avaliação
                    if 'All evaluation functions passed successfully' in text:
                        if 'initial' in text.lower() or 'Initial' in text:
                            data['evaluation_results']['initial_passed'] = True
                        elif 'revised' in text.lower() or 'Revised' in text:
                            data['evaluation_results']['revised_passed'] = True
                    
                    # Extrair falhas de avaliação
                    if 'failures' in text and '[' in text:
                        failures_match = re.search(r'failures=\[(.*?)\]', text)
                        if failures_match:
                            failures_text = failures_match.group(1)
                            if failures_text.strip():
                                failures = [f.strip().strip("'\"") for f in failures_text.split(',')]
                                if 'initial' in text.lower():
                                    data['evaluation_results']['initial_failures'] = failures
                                elif 'revised' in text.lower():
                                    data['evaluation_results']['revised_failures'] = failures
    
    return data

def analyze_itinerary_quality(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa a qualidade do itinerário."""
    
    analysis = {
        'cost_accuracy': {
            'initial': {
                'stated': data['initial_itinerary']['total_cost'],
                'calculated': data['initial_itinerary']['calculated_cost'],
                'accuracy': None
            },
            'revised': {
                'stated': data['revised_itinerary']['total_cost'],
                'calculated': data['revised_itinerary']['calculated_cost'],
                'accuracy': None
            }
        },
        'activity_distribution': {
            'initial': {},
            'revised': {}
        },
        'evaluation_success': {
            'initial_passed': data['evaluation_results']['initial_passed'],
            'revised_passed': data['evaluation_results']['revised_passed'],
            'improvement': None
        }
    }
    
    # Calcular precisão de custo
    if data['initial_itinerary']['total_cost'] and data['initial_itinerary']['calculated_cost']:
        analysis['cost_accuracy']['initial']['accuracy'] = abs(
            data['initial_itinerary']['total_cost'] - data['initial_itinerary']['calculated_cost']
        )
    
    if data['revised_itinerary']['total_cost'] and data['revised_itinerary']['calculated_cost']:
        analysis['cost_accuracy']['revised']['accuracy'] = abs(
            data['revised_itinerary']['total_cost'] - data['revised_itinerary']['calculated_cost']
        )
    
    # Analisar distribuição de atividades
    for day in data['initial_itinerary']['days']:
        date = day['date']
        activity_count = len(day['activities'])
        analysis['activity_distribution']['initial'][date] = activity_count
    
    for day in data['revised_itinerary']['days']:
        date = day['date']
        activity_count = len(day['activities'])
        analysis['activity_distribution']['revised'][date] = activity_count
    
    # Calcular melhoria na avaliação
    initial_passed = data['evaluation_results']['initial_passed']
    revised_passed = data['evaluation_results']['revised_passed']
    
    if initial_passed and revised_passed:
        analysis['evaluation_success']['improvement'] = 'both_passed'
    elif not initial_passed and revised_passed:
        analysis['evaluation_success']['improvement'] = 'improved'
    elif initial_passed and not revised_passed:
        analysis['evaluation_success']['improvement'] = 'regressed'
    else:
        analysis['evaluation_success']['improvement'] = 'both_failed'
    
    return analysis

def print_detailed_analysis(original_data: Dict[str, Any], improved_data: Dict[str, Any]):
    """Imprime análise detalhada."""
    
    print("=" * 100)
    print("🔍 ANÁLISE DETALHADA DOS ITINERÁRIOS")
    print("=" * 100)
    
    # Análise de custo
    print("\n💰 ANÁLISE DE PRECISÃO DE CUSTO:")
    print("-" * 50)
    
    orig_cost = original_data['initial_itinerary']
    impr_cost = improved_data['initial_itinerary']
    
    print(f"📊 VERSÃO ORIGINAL:")
    print(f"   • Custo declarado: {orig_cost['total_cost']}")
    print(f"   • Custo calculado: {orig_cost['calculated_cost']}")
    if orig_cost['total_cost'] and orig_cost['calculated_cost']:
        diff_orig = abs(orig_cost['total_cost'] - orig_cost['calculated_cost'])
        print(f"   • Diferença: {diff_orig}")
    
    print(f"\n📊 VERSÃO MELHORADA:")
    print(f"   • Custo declarado: {impr_cost['total_cost']}")
    print(f"   • Custo calculado: {impr_cost['calculated_cost']}")
    if impr_cost['total_cost'] and impr_cost['calculated_cost']:
        diff_impr = abs(impr_cost['total_cost'] - impr_cost['calculated_cost'])
        print(f"   • Diferença: {diff_impr}")
        
        if diff_orig and diff_impr:
            if diff_impr < diff_orig:
                print(f"   ✅ MELHORIA: Precisão de custo melhorou em {diff_orig - diff_impr} pontos")
            elif diff_impr > diff_orig:
                print(f"   ⚠️ REGRESSÃO: Precisão de custo piorou em {diff_impr - diff_orig} pontos")
            else:
                print(f"   ➡️ NEUTRO: Precisão de custo mantida")
    
    # Análise de distribuição de atividades
    print(f"\n🎪 ANÁLISE DE DISTRIBUIÇÃO DE ATIVIDADES:")
    print("-" * 50)
    
    orig_days = original_data['initial_itinerary']['days']
    impr_days = improved_data['initial_itinerary']['days']
    
    print(f"📊 VERSÃO ORIGINAL:")
    total_activities_orig = 0
    for day in orig_days:
        activity_count = len(day['activities'])
        total_activities_orig += activity_count
        print(f"   • {day['date']}: {activity_count} atividades")
    print(f"   • Total: {total_activities_orig} atividades")
    
    print(f"\n📊 VERSÃO MELHORADA:")
    total_activities_impr = 0
    for day in impr_days:
        activity_count = len(day['activities'])
        total_activities_impr += activity_count
        print(f"   • {day['date']}: {activity_count} atividades")
    print(f"   • Total: {total_activities_impr} atividades")
    
    if total_activities_impr > total_activities_orig:
        print(f"   ✅ MELHORIA: {total_activities_impr - total_activities_orig} atividades adicionais")
    elif total_activities_impr < total_activities_orig:
        print(f"   ⚠️ REGRESSÃO: {total_activities_orig - total_activities_impr} atividades removidas")
    else:
        print(f"   ➡️ NEUTRO: Mesmo número total de atividades")
    
    # Análise de avaliações
    print(f"\n✅ ANÁLISE DE AVALIAÇÕES:")
    print("-" * 50)
    
    orig_eval = original_data['evaluation_results']
    impr_eval = improved_data['evaluation_results']
    
    print(f"📊 VERSÃO ORIGINAL:")
    print(f"   • Avaliações passaram: {'✅ Sim' if orig_eval['initial_passed'] else '❌ Não'}")
    if orig_eval['initial_failures']:
        print(f"   • Falhas: {', '.join(orig_eval['initial_failures'])}")
    
    print(f"\n📊 VERSÃO MELHORADA:")
    print(f"   • Avaliações passaram: {'✅ Sim' if impr_eval['revised_passed'] else '❌ Não'}")
    if impr_eval['revised_failures']:
        print(f"   • Falhas: {', '.join(impr_eval['revised_failures'])}")
    
    # Conclusão
    print(f"\n" + "=" * 100)
    print("📈 CONCLUSÃO DETALHADA:")
    
    improvements = []
    regressions = []
    
    # Verificar melhorias de custo
    if orig_cost['total_cost'] and orig_cost['calculated_cost'] and impr_cost['total_cost'] and impr_cost['calculated_cost']:
        diff_orig = abs(orig_cost['total_cost'] - orig_cost['calculated_cost'])
        diff_impr = abs(impr_cost['total_cost'] - impr_cost['calculated_cost'])
        if diff_impr < diff_orig:
            improvements.append(f"Precisão de custo melhorou em {diff_orig - diff_impr} pontos")
        elif diff_impr > diff_orig:
            regressions.append(f"Precisão de custo piorou em {diff_impr - diff_orig} pontos")
    
    # Verificar melhorias de atividades
    if total_activities_impr > total_activities_orig:
        improvements.append(f"{total_activities_impr - total_activities_orig} atividades adicionais")
    elif total_activities_impr < total_activities_orig:
        regressions.append(f"{total_activities_orig - total_activities_impr} atividades removidas")
    
    # Verificar melhorias de avaliação
    if not orig_eval['initial_passed'] and impr_eval['revised_passed']:
        improvements.append("Avaliações passaram de falha para sucesso")
    elif orig_eval['initial_passed'] and not impr_eval['revised_passed']:
        regressions.append("Avaliações passaram de sucesso para falha")
    
    if improvements:
        print("✅ MELHORIAS IDENTIFICADAS:")
        for improvement in improvements:
            print(f"   • {improvement}")
    
    if regressions:
        print("\n⚠️ REGRESSÕES IDENTIFICADAS:")
        for regression in regressions:
            print(f"   • {regression}")
    
    if not improvements and not regressions:
        print("➡️ Nenhuma mudança significativa identificada")
    
    print("=" * 100)

if __name__ == "__main__":
    # Extrair dados dos notebooks
    original_data = extract_detailed_itinerary_data('project_starter_final_version.ipynb')
    improved_data = extract_detailed_itinerary_data('project_starter_on_revision_executed.ipynb')
    
    # Imprimir análise detalhada
    print_detailed_analysis(original_data, improved_data)
