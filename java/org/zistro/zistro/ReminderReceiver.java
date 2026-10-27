package org.zistro.zistro;

import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import java.util.HashSet;
import java.util.Set;

public class ReminderReceiver extends BroadcastReceiver {
    static final String CHANNEL_ID = "zistro_reminders";
    static final String PREFS = "zistro_alarms";
    static final long WEEK = 7L * 24 * 60 * 60 * 1000;

    @Override
    public void onReceive(Context context, Intent intent) {
        String title = intent.getStringExtra("title");
        String body = intent.getStringExtra("body");
        int code = intent.getIntExtra("code", 0);
        long when = intent.getLongExtra("when", 0);

        NotificationManager nm =
            (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(
                CHANNEL_ID, "Reminders", NotificationManager.IMPORTANCE_HIGH);
            nm.createNotificationChannel(ch);
        }

        Intent launch = context.getPackageManager()
            .getLaunchIntentForPackage(context.getPackageName());
        PendingIntent open = PendingIntent.getActivity(
            context, code, launch,
            PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Notification.Builder b = (Build.VERSION.SDK_INT >= 26)
            ? new Notification.Builder(context, CHANNEL_ID)
            : new Notification.Builder(context);
        b.setContentTitle(title)
         .setContentText(body)
         .setStyle(new Notification.BigTextStyle().bigText(body))
         .setSmallIcon(context.getApplicationInfo().icon)
         .setContentIntent(open)
         .setAutoCancel(true);
        nm.notify(code, b.build());

        // آلارم هفته بعد
        schedule(context, title, body, code, when + WEEK);
    }

    public static void schedule(Context ctx, String title, String body, int code, long when) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);

        Intent i = new Intent(ctx, ReminderReceiver.class);
        i.putExtra("title", title);
        i.putExtra("body", body);
        i.putExtra("code", code);
        i.putExtra("when", when);
        PendingIntent pi = PendingIntent.getBroadcast(
            ctx, code, i,
            PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        if (Build.VERSION.SDK_INT >= 31 && !am.canScheduleExactAlarms()) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, when, pi);   // غیر دقیق
        } else {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, when, pi);
        }

        SharedPreferences sp = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        Set<String> codes = new HashSet<String>(sp.getStringSet("codes", new HashSet<String>()));
        codes.add(String.valueOf(code));
        sp.edit().putStringSet("codes", codes).apply();
    }

    public static void cancelAll(Context ctx) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        SharedPreferences sp = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        Set<String> codes = new HashSet<String>(sp.getStringSet("codes", new HashSet<String>()));
        for (String c : codes) {
            Intent i = new Intent(ctx, ReminderReceiver.class);
            PendingIntent pi = PendingIntent.getBroadcast(
                ctx, Integer.parseInt(c), i,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_NO_CREATE);
            if (pi != null) {
                am.cancel(pi);
                pi.cancel();
            }
        }
        sp.edit().remove("codes").apply();
    }
}
