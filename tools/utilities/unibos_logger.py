#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 unibos logger - genel logging sistemi
tüm sistem olaylarını, hataları ve işlemleri kaydetme

Author: berk hatırlı
Version: v121
Purpose: Merkezi logging altyapısı
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from enum import Enum


class LogLevel(Enum):
    """log seviyeleri"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"


class LogCategory(Enum):
    """log kategorileri"""
    SYSTEM = "system"
    CLAUDE = "claude"
    MODULE = "module"
    API = "api"
    DATABASE = "database"
    UI = "ui"
    SECURITY = "security"
    PERFORMANCE = "performance"
    USER = "user"
    VERSION = "version"


class UnibosLogger:
    """merkezi logging sistemi"""
    
    def __init__(self, log_file: str = "unibos.log"):
        """logger'ı başlat"""
        self.log_file = Path(log_file)
        self.max_size = 10 * 1024 * 1024  # 10MB
        self.max_entries = 10000
        self.rotation_count = 5
        
        # log dosyasını oluştur
        if not self.log_file.exists():
            self._create_log_file()
        
        # boyut kontrolü
        self._check_rotation()
    
    def _create_log_file(self):
        """boş log dosyası oluştur"""
        initial_data = {
            "created": datetime.now().isoformat(),
            "version": "v121",
            "entries": []
        }
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def _check_rotation(self):
        """log dosyası boyutunu kontrol et ve gerekirse rotate et"""
        if self.log_file.exists():
            size = self.log_file.stat().st_size
            if size > self.max_size:
                self._rotate_logs()
    
    def _rotate_logs(self):
        """log dosyalarını rotate et"""
        # mevcut rotated dosyaları kaydır
        for i in range(self.rotation_count - 1, 0, -1):
            old_file = Path(f"{self.log_file}.{i}")
            new_file = Path(f"{self.log_file}.{i + 1}")
            if old_file.exists():
                if new_file.exists():
                    new_file.unlink()
                old_file.rename(new_file)
        
        # mevcut log'u .1 olarak kaydet
        if self.log_file.exists():
            self.log_file.rename(f"{self.log_file}.1")
        
        # yeni log dosyası oluştur
        self._create_log_file()
    
    def log(self,
            level: LogLevel,
            category: LogCategory,
            message: str,
            details: Optional[Dict[str, Any]] = None,
            module: Optional[str] = None,
            function: Optional[str] = None) -> None:
        """genel log kaydı"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "category": category.value,
            "message": message,
            "details": details or {},
            "module": module,
            "function": function,
            "session_id": os.getpid()
        }
        
        # log dosyasını oku
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            self._create_log_file()
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # yeni entry'yi ekle
        data["entries"].append(entry)
        
        # maksimum entry sayısını kontrol et
        if len(data["entries"]) > self.max_entries:
            data["entries"] = data["entries"][-self.max_entries:]
        
        # dosyaya yaz
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # boyut kontrolü
        self._check_rotation()
    
    # kısayol metodlar
    def debug(self, message: str, **kwargs):
        """debug log"""
        category = kwargs.pop('category', LogCategory.SYSTEM)
        self.log(LogLevel.DEBUG, category, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """info log"""
        category = kwargs.pop('category', LogCategory.SYSTEM)
        self.log(LogLevel.INFO, category, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """warning log"""
        category = kwargs.pop('category', LogCategory.SYSTEM)
        self.log(LogLevel.WARNING, category, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """error log"""
        category = kwargs.pop('category', LogCategory.SYSTEM)
        self.log(LogLevel.ERROR, category, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """critical log"""
        category = kwargs.pop('category', LogCategory.SYSTEM)
        self.log(LogLevel.CRITICAL, category, message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """success log"""
        category = kwargs.pop('category', LogCategory.SYSTEM)
        self.log(LogLevel.SUCCESS, category, message, **kwargs)
    
    # özel log metodları
    def log_claude_interaction(self, 
                              action: str, 
                              prompt: Optional[str] = None,
                              response: Optional[str] = None,
                              error: Optional[str] = None):
        """claude etkileşimlerini logla"""
        details = {
            "action": action,
            "prompt_length": len(prompt) if prompt else 0,
            "response_length": len(response) if response else 0,
            "has_error": bool(error)
        }
        if error:
            details["error"] = error
        
        level = LogLevel.ERROR if error else LogLevel.INFO
        self.log(level, LogCategory.CLAUDE, f"Claude {action}", details)
    
    def log_module_event(self,
                        module_name: str,
                        event: str,
                        success: bool = True,
                        details: Optional[Dict] = None):
        """modül olaylarını logla"""
        level = LogLevel.SUCCESS if success else LogLevel.ERROR
        message = f"{module_name}: {event}"
        self.log(level, LogCategory.MODULE, message, details, module=module_name)
    
    def log_api_call(self,
                    endpoint: str,
                    method: str = "GET",
                    status_code: Optional[int] = None,
                    response_time: Optional[float] = None,
                    error: Optional[str] = None):
        """api çağrılarını logla"""
        details = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "success": 200 <= status_code < 300 if status_code else False
        }
        if error:
            details["error"] = error
        
        level = LogLevel.INFO if details["success"] else LogLevel.ERROR
        message = f"API {method} {endpoint}"
        self.log(level, LogCategory.API, message, details)
    
    def log_performance(self,
                       operation: str,
                       duration: float,
                       details: Optional[Dict] = None):
        """performans metriklerini logla"""
        perf_details = {
            "duration_ms": round(duration * 1000, 2),
            "slow": duration > 1.0  # 1 saniyeden uzun işlemler
        }
        if details:
            perf_details.update(details)
        
        level = LogLevel.WARNING if perf_details["slow"] else LogLevel.INFO
        message = f"Performance: {operation} ({perf_details['duration_ms']}ms)"
        self.log(level, LogCategory.PERFORMANCE, message, perf_details)
    
    def log_security_event(self,
                          event_type: str,
                          severity: str = "medium",
                          details: Optional[Dict] = None):
        """güvenlik olaylarını logla"""
        sec_details = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": time.time()
        }
        if details:
            sec_details.update(details)
        
        level = LogLevel.CRITICAL if severity == "high" else LogLevel.WARNING
        message = f"Security: {event_type}"
        self.log(level, LogCategory.SECURITY, message, sec_details)
    
    def log_version_change(self,
                          old_version: str,
                          new_version: str,
                          changes: List[str]):
        """versiyon değişikliklerini logla"""
        details = {
            "old_version": old_version,
            "new_version": new_version,
            "changes": changes,
            "change_count": len(changes)
        }
        message = f"Version update: {old_version} -> {new_version}"
        self.log(LogLevel.INFO, LogCategory.VERSION, message, details)
    
    def get_recent_logs(self,
                       count: int = 100,
                       level: Optional[LogLevel] = None,
                       category: Optional[LogCategory] = None) -> List[Dict]:
        """son logları getir"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entries = data.get("entries", [])
            
            # filtreleme
            if level:
                entries = [e for e in entries if e.get("level") == level.value]
            if category:
                entries = [e for e in entries if e.get("category") == category.value]
            
            # son N kaydı döndür
            return entries[-count:]
        except:
            return []
    
    def get_error_summary(self) -> Dict[str, int]:
        """hata özetini getir"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            summary = {}
            for entry in data.get("entries", []):
                if entry.get("level") in ["error", "critical"]:
                    category = entry.get("category", "unknown")
                    summary[category] = summary.get(category, 0) + 1
            
            return summary
        except:
            return {}
    
    def clear_old_logs(self, days: int = 30):
        """eski logları temizle"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # eski entry'leri filtrele
            data["entries"] = [
                e for e in data.get("entries", [])
                if datetime.fromisoformat(e.get("timestamp", "")) > cutoff
            ]
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return len(data["entries"])
        except:
            return 0


# global logger instance
logger = UnibosLogger()


# performans decorator
def log_performance(operation_name: str):
    """fonksiyon performansını loglamak için decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_performance(
                    f"{operation_name} ({func.__name__})",
                    duration,
                    {"function": func.__name__, "module": func.__module__}
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Performance decorator error: {operation_name}",
                    details={
                        "function": func.__name__,
                        "error": str(e),
                        "duration": duration
                    }
                )
                raise
        return wrapper
    return decorator


# kullanım örnekleri
if __name__ == "__main__":
    # test logları
    logger.info("Logger sistemi başlatıldı", category=LogCategory.SYSTEM)
    logger.success("Test başarılı", details={"test": "initial"})
    logger.warning("Dikkat edilmesi gereken durum", category=LogCategory.MODULE)
    logger.error("Test hatası", details={"code": 500}, category=LogCategory.API)
    
    # özel loglar
    logger.log_claude_interaction("chat", prompt="test prompt", response="test response")
    logger.log_api_call("/api/currencies", "GET", 200, 0.234)
    logger.log_performance("database_query", 0.156)
    logger.log_security_event("unauthorized_access", "high", {"ip": "127.0.0.1"})
    
    print("✅ Logger test tamamlandı. unibos.log dosyasını kontrol edin.")