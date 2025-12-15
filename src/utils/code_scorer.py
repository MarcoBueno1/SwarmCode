# SPDX-License-Identifier: MIT
# Copyright (C) 2026 Marco Antônio Bueno da Silva <bueno.marco@gmail.com>
#
# This file is part of SwarmCode.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Code Quality Scoring for SwarmCode.

Provides multi-criteria code quality evaluation.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class QualityScore:
    """Quality score for a code artifact."""
    maintainability: float = 0.0  # 0-10
    security: float = 0.0  # 0-10
    performance: float = 0.0  # 0-10
    documentation: float = 0.0  # 0-10
    testing: float = 0.0  # 0-10
    
    @property
    def overall(self) -> float:
        """Calculate overall score (weighted average)."""
        weights = {
            'maintainability': 0.25,
            'security': 0.25,
            'performance': 0.15,
            'documentation': 0.20,
            'testing': 0.15,
        }
        return (
            self.maintainability * weights['maintainability'] +
            self.security * weights['security'] +
            self.performance * weights['performance'] +
            self.documentation * weights['documentation'] +
            self.testing * weights['testing']
        )
    
    def stars(self) -> str:
        """Return star rating."""
        overall = self.overall
        if overall >= 9.0:
            return "⭐⭐⭐⭐⭐"
        elif overall >= 7.0:
            return "⭐⭐⭐⭐"
        elif overall >= 5.0:
            return "⭐⭐⭐"
        elif overall >= 3.0:
            return "⭐⭐"
        else:
            return "⭐"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'overall': round(self.overall, 1),
            'maintainability': round(self.maintainability, 1),
            'security': round(self.security, 1),
            'performance': round(self.performance, 1),
            'documentation': round(self.documentation, 1),
            'testing': round(self.testing, 1),
            'stars': self.stars(),
        }


class CodeQualityScorer:
    """Calculates code quality scores."""
    
    def __init__(self):
        pass
    
    def score(self, code: str, has_tests: bool = False, has_docs: bool = False) -> QualityScore:
        """
        Calculate quality score for code.
        
        Args:
            code: Source code to analyze
            has_tests: Whether tests were generated
            has_docs: Whether documentation was generated
        
        Returns:
            QualityScore with all metrics
        """
        score = QualityScore()
        
        # Maintainability score
        score.maintainability = self._calc_maintainability(code)
        
        # Security score
        score.security = self._calc_security(code)
        
        # Performance score
        score.performance = self._calc_performance(code)
        
        # Documentation score
        score.documentation = self._calc_documentation(code, has_docs)
        
        # Testing score
        score.testing = self._calc_testing(code, has_tests)
        
        return score
    
    def _calc_maintainability(self, code: str) -> float:
        """
        Calculate maintainability score.
        
        Factors:
        - Function length (shorter is better)
        - Cyclomatic complexity (lower is better)
        - Code duplication (lower is better)
        - Naming conventions (consistent is better)
        """
        score = 10.0
        
        # Check function length
        functions = re.findall(r'def\s+\w+\s*\([^)]*\)\s*:', code)
        if len(functions) > 0:
            # Average function length penalty
            lines = code.split('\n')
            avg_lines_per_func = len(lines) / len(functions)
            if avg_lines_per_func > 50:
                score -= min(3, (avg_lines_per_func - 50) / 20)
        
        # Check for type hints (good for maintainability)
        if ': ' in code and '->' in code:
            score += 1.0  # Bonus for type hints
        
        # Check for consistent naming (snake_case for functions)
        func_names = re.findall(r'def\s+(\w+)\s*\(', code)
        snake_case_count = sum(1 for name in func_names if name.islower() or '_' in name)
        if func_names:
            snake_case_ratio = snake_case_count / len(func_names)
            score += snake_case_ratio  # 0-1 bonus
        
        return max(0, min(10, score))
    
    def _calc_security(self, code: str) -> float:
        """
        Calculate security score.
        
        Factors:
        - No hardcoded secrets
        - Input validation present
        - No dangerous functions (eval, exec)
        - Error handling present
        """
        score = 10.0
        
        # Check for dangerous functions
        dangerous = ['eval(', 'exec(', 'os.system(', 'subprocess.call(', 'pickle.load(']
        for danger in dangerous:
            if danger in code:
                score -= 2.0
        
        # Check for hardcoded secrets (basic check)
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ]
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                score -= 2.0
        
        # Check for input validation
        if 'if ' in code and 'raise' in code:
            score += 0.5  # Bonus for validation
        
        # Check for try/except (error handling)
        if 'try:' in code and 'except' in code:
            score += 0.5  # Bonus for error handling
        
        return max(0, min(10, score))
    
    def _calc_performance(self, code: str) -> float:
        """
        Calculate performance score.
        
        Factors:
        - No obvious performance issues
        - Efficient data structures
        - No unnecessary loops
        """
        score = 10.0
        
        # Check for nested loops (O(n²) or worse)
        nested_loops = code.count('for ') + code.count('while ')
        if nested_loops > 5:
            score -= min(3, (nested_loops - 5) * 0.5)
        
        # Check for list comprehensions (good for performance)
        if '[' in code and 'for' in code and 'in' in code:
            score += 0.5  # Bonus for comprehensions
        
        # Check for generators (excellent for memory)
        if 'yield' in code:
            score += 1.0  # Bonus for generators
        
        return max(0, min(10, score))
    
    def _calc_documentation(self, code: str, has_docs: bool) -> float:
        """
        Calculate documentation score.
        
        Factors:
        - Docstrings present
        - Comments for complex logic
        - README or external docs
        """
        score = 5.0  # Base score
        
        # Check for docstrings
        docstring_count = code.count('"""') + code.count("'''")
        if docstring_count >= 2:
            score += 2.0  # Has docstrings
        if docstring_count >= 6:
            score += 1.0  # Well documented
        
        # Check for inline comments
        comment_count = code.count('# ')
        if comment_count > 5:
            score += 1.0  # Has comments
        if comment_count > 15:
            score += 1.0  # Well commented
        
        # Bonus for external documentation
        if has_docs:
            score += 2.0
        
        return max(0, min(10, score))
    
    def _calc_testing(self, code: str, has_tests: bool) -> float:
        """
        Calculate testing score.
        
        Factors:
        - Tests generated
        - Test coverage estimation
        """
        if has_tests:
            return 10.0  # Full score if tests exist
        else:
            return 3.0  # Low score without tests
