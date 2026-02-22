package org.helpchildren.amharic

import android.app.Application

class AmharicAssistantApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        instance = this
    }
    
    companion object {
        lateinit var instance: AmharicAssistantApp
            private set
    }
}
