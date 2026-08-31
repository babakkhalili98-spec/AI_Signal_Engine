"""
اینترفیس‌های پایه برای Providerهای داده بازار.
این ماژول لایه انتزاع (Abstraction Layer) را برای دریافت داده از منابع مختلف تعریف می‌کند.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from models.asset import Instrument, AssetClass, MarketRegion
from models.market_data import Candle, Ticker


class IMarketProvider(ABC):
    """
    اینترفیس پایه برای تمام Providerهای داده بازار.
    
    هر Provider (Nobitex, Binance, Forex Provider, Stock Data Provider, etc.)
    باید این اینترفیس را پیاده‌سازی کند.
    """
    
    @abstractmethod
    def get_supported_assets(self) -> List[AssetClass]:
        """
       返回列表支持的资产类别。
        
        Returns:
            List[AssetClass]: لیست کلاس‌های دارایی پشتیبانی‌شده
        """
        pass
    
    @abstractmethod
    def supports_region(self, region: MarketRegion) -> bool:
        """
        بررسی می‌کند که آیا Provider از منطقه خاصی پشتیبانی می‌کند.
        
        Args:
            region: منطقه مورد نظر
            
        Returns:
            bool: True اگر پشتیبانی شود
        """
        pass
    
    @abstractmethod
    def get_instrument_metadata(self, instrument_id: str) -> Optional[Instrument]:
        """
        دریافت متادیتای کامل یک دارایی.
        
        Args:
            instrument_id: شناسه یکتای دارایی (مثلاً CRYPTO:NOBITEX:BTCUSDT)
            
        Returns:
            Optional[Instrument]: شیء Instrument یا None اگر یافت نشد
        """
        pass
    
    @abstractmethod
    def get_candles(
        self,
        instrument_id: str,
        timeframe: str,
        limit: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Candle]:
        """
        دریافت داده‌های تاریخی کندل‌ها.
        
        Args:
            instrument_id: شناسه یکتای دارایی
            timeframe: تایم‌فریم (مثلاً "1h", "4h", "1d")
            limit: تعداد کندل‌های مورد نیاز
            start_time: زمان شروع (اختیاری)
            end_time: زمان پایان (اختیاری)
            
        Returns:
            List[Candle]: لیستی از اشیاء Candle
        """
        pass
    
    @abstractmethod
    def get_ticker(self, instrument_id: str) -> Optional[Ticker]:
        """
        دریافت اطلاعات قیمت لحظه‌ای (Ticker).
        
        Args:
            instrument_id: شناسه یکتای دارایی
            
        Returns:
            Optional[Ticker]: شیء Ticker یا None
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        بررسی در دسترس بودن Provider.
        
        Returns:
            bool: True اگر Provider در دسترس باشد
        """
        pass


class MarketProviderRegistry:
    """
    Registry برای ثبت و مدیریت Providerهای مختلف.
    
    این کلاس امکان افزودن Providerهای جدید و بازیابی آن‌ها بر اساس
    کلاس دارایی و منطقه را فراهم می‌کند.
    """
    
    _providers: dict[str, IMarketProvider] = {}
    
    @classmethod
    def register(cls, name: str, provider: IMarketProvider):
        """
        ثبت یک Provider جدید.
        
        Args:
            name: نام منحصر به فرد Provider
            provider: شیء Provider
        """
        cls._providers[name] = provider
    
    @classmethod
    def get(cls, name: str) -> Optional[IMarketProvider]:
        """
        دریافت یک Provider بر اساس نام.
        
        Args:
            name: نام Provider
            
        Returns:
            Optional[IMarketProvider]: شیء Provider یا None
        """
        return cls._providers.get(name)
    
    @classmethod
    def get_provider_for_asset(
        cls,
        asset_class: AssetClass,
        region: MarketRegion
    ) -> Optional[IMarketProvider]:
        """
        دریافت مناسب‌ترین Provider برای یک کلاس دارایی و منطقه.
        
        Args:
            asset_class: کلاس دارایی
            region: منطقه بازار
            
        Returns:
            Optional[IMarketProvider]: Provider مناسب یا None
        """
        for provider in cls._providers.values():
            if asset_class in provider.get_supported_assets():
                if provider.supports_region(region):
                    return provider
        return None
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """
       返回列表所有已注册的提供者名称。
        
        Returns:
            List[str]: لیست نام Providerهای ثبت‌شده
        """
        return list(cls._providers.keys())
