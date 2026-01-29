package com.foqos.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverters
import com.foqos.data.local.Converters
import java.util.UUID

@Entity(tableName = "blocked_profiles")
@TypeConverters(Converters::class)
data class BlockedProfileEntity(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val selectedApps: List<String> = emptyList(), // Package names
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis(),
    val blockingStrategyId: String = "nfc",
    val strategyData: String? = null, // JSON serialized strategy-specific data
    val order: Int = 0,
    
    // Features
    val enableLiveNotification: Boolean = true,
    val reminderTimeInSeconds: Int? = null,
    val customReminderMessage: String? = null,
    val enableBreaks: Boolean = false,
    val breakTimeInMinutes: Int = 15,
    val enableStrictMode: Boolean = false,
    val enableAllowMode: Boolean = false,
    val enableAllowModeDomains: Boolean = false,
    val enableWebBlocking: Boolean = true,
    
    // Website blocking
    val domains: List<String>? = null,
    
    // Physical unlock
    val physicalUnblockNFCTagId: String? = null,
    val physicalUnblockQRCodeId: String? = null,
    
    // Schedule
    val scheduleEnabled: Boolean = false,
    val scheduleDaysOfWeek: List<Int>? = null, // 1=Monday, 7=Sunday
    val scheduleStartTime: String? = null, // HH:mm format
    val scheduleEndTime: String? = null, // HH:mm format
    
    val disableBackgroundStops: Boolean = false
)
