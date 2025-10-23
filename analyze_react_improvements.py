#!/usr/bin/env python3
"""
Script para analisar as melhorias do ReAct Agent
"""

import json
import re
from typing import Dict, List, Any

def analyze_react_agent_improvements(notebook_path: str) -> Dict[str, Any]:
    """Analisa as melhorias do ReAct Agent no notebook."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    analysis = {
        'react_cycle_completion': {
            'run_evals_tool_called': False,
            'final_answer_tool_called': False,
            'proper_sequence': False,
            'successful_evaluation': False
        },
        'tool_usage': {
            'get_activities_by_date_tool': 0,
            'calculator_tool': 0,
            'run_evals_tool': 0,
            'final_answer_tool': 0
        },
        'evaluation_results': {
            'initial_failures': [],
            'final_success': False,
            'improvement_steps': 0
        },
        'react_steps': []
    }
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code' and 'outputs' in cell:
            for output in cell['outputs']:
                if output.get('output_type') == 'stream':
                    text = ''.join(output.get('text', []))
                    
                    # Verificar se run_evals_tool foi chamado
                    if 'OBSERVATION: Tool run_evals_tool called successfully' in text:
                        analysis['react_cycle_completion']['run_evals_tool_called'] = True
                        analysis['tool_usage']['run_evals_tool'] += 1
                        
                        # Extrair resultado da avaliação
                        if "'success': True" in text:
                            analysis['react_cycle_completion']['successful_evaluation'] = True
                            analysis['evaluation_results']['final_success'] = True
                        elif "'success': False" in text:
                            # Extrair falhas
                            failures_match = re.search(r"'failures': \[(.*?)\]", text)
                            if failures_match:
                                failures_text = failures_match.group(1)
                                if failures_text.strip():
                                    failures = [f.strip().strip("'\"") for f in failures_text.split(',')]
                                    analysis['evaluation_results']['initial_failures'] = failures
                    
                    # Verificar se final_answer_tool foi chamado
                    if 'OBSERVATION: Tool final_answer_tool called successfully' in text:
                        analysis['react_cycle_completion']['final_answer_tool_called'] = True
                        analysis['tool_usage']['final_answer_tool'] += 1
                    
                    # Contar uso de outras ferramentas
                    if 'OBSERVATION: Tool get_activities_by_date_tool called successfully' in text:
                        analysis['tool_usage']['get_activities_by_date_tool'] += 1
                    
                    if 'OBSERVATION: Tool calculator_tool called successfully' in text:
                        analysis['tool_usage']['calculator_tool'] += 1
                    
                    # Extrair passos do ReAct
                    if 'THOUGHT:' in text and 'ACTION:' in text:
                        thought_match = re.search(r'THOUGHT: (.*?)(?=ACTION:|$)', text, re.DOTALL)
                        action_match = re.search(r'ACTION: (.*?)(?=THOUGHT:|$)', text, re.DOTALL)
                        
                        if thought_match and action_match:
                            step = {
                                'thought': thought_match.group(1).strip(),
                                'action': action_match.group(1).strip()
                            }
                            analysis['react_steps'].append(step)
    
    # Verificar se a sequência foi adequada
    if (analysis['react_cycle_completion']['run_evals_tool_called'] and 
        analysis['react_cycle_completion']['final_answer_tool_called'] and
        analysis['react_cycle_completion']['successful_evaluation']):
        analysis['react_cycle_completion']['proper_sequence'] = True
    
    # Contar passos de melhoria
    analysis['evaluation_results']['improvement_steps'] = len(analysis['react_steps'])
    
    return analysis

def print_react_analysis_report(analysis: Dict[str, Any]):
    """Imprime relatório de análise do ReAct Agent."""
    
    print("=" * 100)
    print("🔍 ANÁLISE DAS MELHORIAS DO REACT AGENT")
    print("=" * 100)
    
    print("\n🎯 COMPLETUDE DO CICLO REACT:")
    print("-" * 50)
    
    completion = analysis['react_cycle_completion']
    
    print(f"✅ run_evals_tool foi chamado: {'✅ Sim' if completion['run_evals_tool_called'] else '❌ Não'}")
    print(f"✅ final_answer_tool foi chamado: {'✅ Sim' if completion['final_answer_tool_called'] else '❌ Não'}")
    print(f"✅ Avaliação bem-sucedida: {'✅ Sim' if completion['successful_evaluation'] else '❌ Não'}")
    print(f"✅ Sequência adequada: {'✅ Sim' if completion['proper_sequence'] else '❌ Não'}")
    
    print(f"\n📊 USO DE FERRAMENTAS:")
    print("-" * 50)
    
    tool_usage = analysis['tool_usage']
    print(f"🔍 get_activities_by_date_tool: {tool_usage['get_activities_by_date_tool']} chamadas")
    print(f"🧮 calculator_tool: {tool_usage['calculator_tool']} chamadas")
    print(f"✅ run_evals_tool: {tool_usage['run_evals_tool']} chamadas")
    print(f"🏁 final_answer_tool: {tool_usage['final_answer_tool']} chamadas")
    
    print(f"\n📈 RESULTADOS DAS AVALIAÇÕES:")
    print("-" * 50)
    
    eval_results = analysis['evaluation_results']
    print(f"🎯 Sucesso final: {'✅ Sim' if eval_results['final_success'] else '❌ Não'}")
    print(f"📝 Passos de melhoria: {eval_results['improvement_steps']}")
    
    if eval_results['initial_failures']:
        print(f"⚠️ Falhas iniciais encontradas:")
        for failure in eval_results['initial_failures']:
            print(f"   • {failure}")
    
    print(f"\n🔄 PASSOS DO CICLO REACT:")
    print("-" * 50)
    
    for i, step in enumerate(analysis['react_steps'], 1):
        print(f"\nPasso {i}:")
        print(f"   💭 THOUGHT: {step['thought'][:100]}...")
        print(f"   🎬 ACTION: {step['action'][:100]}...")
    
    print(f"\n" + "=" * 100)
    print("📊 AVALIAÇÃO DAS MELHORIAS:")
    print("=" * 100)
    
    # Calcular score
    score = 0
    max_score = 4
    
    if completion['run_evals_tool_called']:
        score += 1
        print("✅ MELHORIA 1: run_evals_tool foi chamado adequadamente")
    else:
        print("❌ FALHA 1: run_evals_tool não foi chamado")
    
    if completion['final_answer_tool_called']:
        score += 1
        print("✅ MELHORIA 2: final_answer_tool foi chamado adequadamente")
    else:
        print("❌ FALHA 2: final_answer_tool não foi chamado")
    
    if completion['successful_evaluation']:
        score += 1
        print("✅ MELHORIA 3: Avaliação foi bem-sucedida")
    else:
        print("❌ FALHA 3: Avaliação não foi bem-sucedida")
    
    if completion['proper_sequence']:
        score += 1
        print("✅ MELHORIA 4: Sequência adequada (eval → success → final)")
    else:
        print("❌ FALHA 4: Sequência inadequada")
    
    print(f"\n🎯 SCORE FINAL: {score}/{max_score}")
    
    if score == max_score:
        print("🏆 RESULTADO: TODAS AS MELHORIAS FORAM IMPLEMENTADAS COM SUCESSO!")
    elif score >= 3:
        print("✅ RESULTADO: MAIORIA DAS MELHORIAS FORAM IMPLEMENTADAS")
    elif score >= 2:
        print("⚠️ RESULTADO: ALGUMAS MELHORIAS FORAM IMPLEMENTADAS")
    else:
        print("❌ RESULTADO: POUCAS MELHORIAS FORAM IMPLEMENTADAS")
    
    print("=" * 100)

if __name__ == "__main__":
    # Analisar o notebook com melhorias do ReAct
    analysis = analyze_react_agent_improvements('project_starter_on_revision_react_improved.ipynb')
    
    # Imprimir relatório
    print_react_analysis_report(analysis)
