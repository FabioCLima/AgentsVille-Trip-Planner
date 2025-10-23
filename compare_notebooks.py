#!/usr/bin/env python3
"""
Script para comparar as saídas entre a versão original e a versão melhorada do notebook.
"""

import json
import re
from typing import Dict, List, Any

def extract_travel_plan_data(notebook_path: str) -> Dict[str, Any]:
    """Extrai dados do plano de viagem do notebook."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    data = {
        'initial_cost': None,
        'revised_cost': None,
        'initial_activities_count': 0,
        'revised_activities_count': 0,
        'evaluation_results': [],
        'warnings': [],
        'success_messages': []
    }
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code' and 'outputs' in cell:
            for output in cell['outputs']:
                if output.get('output_type') == 'stream':
                    text = ''.join(output.get('text', []))
                    
                    # Extrair custos
                    cost_match = re.search(r'total_cost \((\d+)\)', text)
                    if cost_match:
                        if 'Initial' in text or 'initial' in text:
                            data['initial_cost'] = int(cost_match.group(1))
                        elif 'Revised' in text or 'revised' in text:
                            data['revised_cost'] = int(cost_match.group(1))
                    
                    # Extrair warnings
                    if 'Warning:' in text:
                        data['warnings'].append(text.strip())
                    
                    # Extrair mensagens de sucesso
                    if '✅' in text:
                        data['success_messages'].append(text.strip())
                    
                    # Contar atividades
                    if 'activity_id' in text:
                        activity_count = len(re.findall(r'event-\d{4}-\d{2}-\d{2}-\d+', text))
                        if 'Initial' in text or 'initial' in text:
                            data['initial_activities_count'] = max(data['initial_activities_count'], activity_count)
                        elif 'Revised' in text or 'revised' in text:
                            data['revised_activities_count'] = max(data['revised_activities_count'], activity_count)
    
    return data

def compare_notebooks(original_path: str, improved_path: str) -> Dict[str, Any]:
    """Compara os dois notebooks e retorna métricas de comparação."""
    
    original_data = extract_travel_plan_data(original_path)
    improved_data = extract_travel_plan_data(improved_path)
    
    comparison = {
        'original': original_data,
        'improved': improved_data,
        'metrics': {
            'cost_accuracy_improvement': None,
            'activity_count_improvement': None,
            'warning_reduction': None,
            'success_rate': None
        }
    }
    
    # Calcular melhorias
    if original_data['initial_cost'] and improved_data['initial_cost']:
        comparison['metrics']['cost_accuracy_improvement'] = {
            'original': original_data['initial_cost'],
            'improved': improved_data['initial_cost'],
            'difference': improved_data['initial_cost'] - original_data['initial_cost']
        }
    
    if original_data['initial_activities_count'] and improved_data['initial_activities_count']:
        comparison['metrics']['activity_count_improvement'] = {
            'original': original_data['initial_activities_count'],
            'improved': improved_data['initial_activities_count'],
            'difference': improved_data['initial_activities_count'] - original_data['initial_activities_count']
        }
    
    comparison['metrics']['warning_reduction'] = {
        'original_warnings': len(original_data['warnings']),
        'improved_warnings': len(improved_data['warnings']),
        'reduction': len(original_data['warnings']) - len(improved_data['warnings'])
    }
    
    comparison['metrics']['success_rate'] = {
        'original_success': len(original_data['success_messages']),
        'improved_success': len(improved_data['success_messages']),
        'improvement': len(improved_data['success_messages']) - len(original_data['success_messages'])
    }
    
    return comparison

def print_comparison_report(comparison: Dict[str, Any]):
    """Imprime um relatório detalhado da comparação."""
    
    print("=" * 80)
    print("📊 RELATÓRIO DE COMPARAÇÃO: VERSÃO ORIGINAL vs VERSÃO MELHORADA")
    print("=" * 80)
    
    print("\n🎯 MÉTRICAS DE QUALIDADE:")
    print("-" * 40)
    
    # Custo
    cost_metric = comparison['metrics']['cost_accuracy_improvement']
    if cost_metric:
        print(f"💰 Precisão de Custo:")
        print(f"   • Original: {cost_metric['original']}")
        print(f"   • Melhorada: {cost_metric['improved']}")
        print(f"   • Diferença: {cost_metric['difference']:+d}")
        if cost_metric['difference'] < 0:
            print("   ✅ MELHORIA: Custo mais preciso (menor)")
        elif cost_metric['difference'] > 0:
            print("   ⚠️ REGRESSÃO: Custo aumentou")
        else:
            print("   ➡️ NEUTRO: Custo mantido")
    
    # Atividades
    activity_metric = comparison['metrics']['activity_count_improvement']
    if activity_metric:
        print(f"\n🎪 Contagem de Atividades:")
        print(f"   • Original: {activity_metric['original']}")
        print(f"   • Melhorada: {activity_metric['improved']}")
        print(f"   • Diferença: {activity_metric['difference']:+d}")
        if activity_metric['difference'] > 0:
            print("   ✅ MELHORIA: Mais atividades incluídas")
        elif activity_metric['difference'] < 0:
            print("   ⚠️ REGRESSÃO: Menos atividades")
        else:
            print("   ➡️ NEUTRO: Mesmo número de atividades")
    
    # Warnings
    warning_metric = comparison['metrics']['warning_reduction']
    print(f"\n⚠️ Redução de Warnings:")
    print(f"   • Original: {warning_metric['original_warnings']}")
    print(f"   • Melhorada: {warning_metric['improved_warnings']}")
    print(f"   • Redução: {warning_metric['reduction']:+d}")
    if warning_metric['reduction'] > 0:
        print("   ✅ MELHORIA: Menos warnings")
    elif warning_metric['reduction'] < 0:
        print("   ⚠️ REGRESSÃO: Mais warnings")
    else:
        print("   ➡️ NEUTRO: Mesmo número de warnings")
    
    # Sucesso
    success_metric = comparison['metrics']['success_rate']
    print(f"\n✅ Taxa de Sucesso:")
    print(f"   • Original: {success_metric['original_success']}")
    print(f"   • Melhorada: {success_metric['improved_success']}")
    print(f"   • Melhoria: {success_metric['improvement']:+d}")
    if success_metric['improvement'] > 0:
        print("   ✅ MELHORIA: Mais mensagens de sucesso")
    elif success_metric['improvement'] < 0:
        print("   ⚠️ REGRESSÃO: Menos mensagens de sucesso")
    else:
        print("   ➡️ NEUTRO: Mesma taxa de sucesso")
    
    print("\n📋 DETALHES DAS VERSÕES:")
    print("-" * 40)
    
    print("\n🔍 VERSÃO ORIGINAL:")
    print(f"   • Warnings: {len(comparison['original']['warnings'])}")
    for warning in comparison['original']['warnings']:
        print(f"     - {warning}")
    
    print("\n🚀 VERSÃO MELHORADA:")
    print(f"   • Warnings: {len(comparison['improved']['warnings'])}")
    for warning in comparison['improved']['warnings']:
        print(f"     - {warning}")
    
    print("\n" + "=" * 80)
    print("📈 CONCLUSÃO GERAL:")
    
    improvements = 0
    regressions = 0
    
    if cost_metric and cost_metric['difference'] < 0:
        improvements += 1
    elif cost_metric and cost_metric['difference'] > 0:
        regressions += 1
    
    if activity_metric and activity_metric['difference'] > 0:
        improvements += 1
    elif activity_metric and activity_metric['difference'] < 0:
        regressions += 1
    
    if warning_metric['reduction'] > 0:
        improvements += 1
    elif warning_metric['reduction'] < 0:
        regressions += 1
    
    if success_metric['improvement'] > 0:
        improvements += 1
    elif success_metric['improvement'] < 0:
        regressions += 1
    
    if improvements > regressions:
        print("✅ RESULTADO: As melhorias foram EFETIVAS!")
        print(f"   • {improvements} melhorias identificadas")
        print(f"   • {regressions} regressões identificadas")
    elif regressions > improvements:
        print("⚠️ RESULTADO: Algumas regressões foram identificadas")
        print(f"   • {improvements} melhorias identificadas")
        print(f"   • {regressions} regressões identificadas")
    else:
        print("➡️ RESULTADO: Melhorias neutras - sem mudanças significativas")
        print(f"   • {improvements} melhorias identificadas")
        print(f"   • {regressions} regressões identificadas")
    
    print("=" * 80)

if __name__ == "__main__":
    # Comparar os notebooks
    comparison = compare_notebooks(
        'project_starter_final_version.ipynb',
        'project_starter_on_revision_executed.ipynb'
    )
    
    # Imprimir relatório
    print_comparison_report(comparison)
